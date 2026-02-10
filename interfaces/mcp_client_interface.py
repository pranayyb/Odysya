import json
import os
from typing import Optional, List
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from config import llm_model
from utils.logger import get_logger
from utils.error_handler import ClientError

from dotenv import load_dotenv

load_dotenv()

logger = get_logger("MCPClient")


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.groq = llm_model
        self.tools: List = []
        self.client_name = "Generic"

    async def connect(self, server_script_path: str):
        logger.info(f"[{self.client_name}] Connecting to server: {server_script_path}")
        try:
            server_params = StdioServerParameters(
                command="uv", args=["run", "-m", server_script_path], env=None
            )

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport

            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )
            await self.session.initialize()

            response = await self.session.list_tools()
            self.tools = response.tools

            logger.info(f"[{self.client_name}] Connected with {len(self.tools)} tools:")
            for tool in self.tools:
                logger.debug(f"  - {tool.name}: {tool.description}")
        except Exception as e:
            logger.error(f"[{self.client_name}] Connection failed: {e}")
            raise ClientError(str(e), client_name=self.client_name)

    def _build_system_prompt(self) -> str:
        tool_names = [tool.name for tool in self.tools]
        return (
            f"You are a {self.client_name} assistant. You have access to these tools: {tool_names}. "
            f"When the user asks a question, call the most appropriate tool with the correct parameters. "
            f"Only use tools that are listed above. Do not invent tool names or parameters."
        )

    def _select_best_tool(self, query: str) -> tuple[str, dict]:
        """Deterministically select the best tool and extract params from the query
        using the LLM, bypassing Groq's unreliable tool_choice mechanism."""
        tool_descriptions = []
        for tool in self.tools:
            schema = json.dumps(tool.inputSchema, indent=2)
            tool_descriptions.append(
                f"Tool: {tool.name}\nDescription: {tool.description}\nParameters schema:\n{schema}"
            )

        selection_prompt = (
            "Given the user query and available tools, respond with ONLY valid JSON (no markdown, no extra text).\n"
            "Pick the single best tool and extract the parameters from the query.\n\n"
            f"Available tools:\n" + "\n---\n".join(tool_descriptions) + "\n\n"
            f"User query: {query}\n\n"
            "Respond with exactly this JSON format:\n"
            '{"tool": "<tool_name>", "args": {<extracted_parameters>}}\n'
            "Rules:\n"
            "- Only use tool names from the list above\n"
            "- Only include parameters defined in the schema\n"
            "- Use correct types (string, number, etc.)\n"
            "- For optional parameters, only include them if the query mentions them"
        )

        response = self.groq.invoke([{"role": "user", "content": selection_prompt}])

        raw = response.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        parsed = json.loads(raw)
        return parsed["tool"], parsed.get("args", {})

    async def process_query(self, query: str) -> str:
        logger.info(f"[{self.client_name}] Processing query: {query[:100]}...")
        try:
            # Step 1: Use LLM to select tool and extract params deterministically
            tool_name, tool_args = self._select_best_tool(query)

            valid_tool_names = {tool.name for tool in self.tools}
            if tool_name not in valid_tool_names:
                logger.warning(
                    f"[{self.client_name}] LLM selected invalid tool '{tool_name}', "
                    f"falling back to first tool"
                )
                tool_name = self.tools[0].name

            logger.info(
                f"[{self.client_name}] Calling tool: {tool_name} | args={tool_args}"
            )

            # Step 2: Call the MCP tool directly
            result = await self.session.call_tool(tool_name, tool_args)
            tool_result = result.content[0].text if result.content else str(result)
            logger.info(
                f"[{self.client_name}] Tool {tool_name} returned {len(tool_result)} chars"
            )

            # Step 3: Summarize the tool output
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Summarize the tool results clearly for the user. "
                        "Do not invent information beyond what the tool returned. "
                        "Only simplify and rephrase."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nTool result:\n{tool_result}",
                },
            ]

            followup = self.groq.invoke(messages)

            summary = followup.content
            logger.info(f"[{self.client_name}] Query processed successfully")
            return summary or tool_result

        except Exception as e:
            logger.error(f"[{self.client_name}] Query processing failed: {e}")
            raise ClientError(str(e), client_name=self.client_name)

    async def chat_loop(self):
        print(f"\n{self.client_name} Client Started! Type 'quit' to exit.")

        while True:
            query = input("\n>> ").strip()
            if query.lower() == "quit":
                break

            try:
                response = await self.process_query(query)
                print("\n--- Result ---")
                print(response)
                print("--------------")
            except Exception as e:
                logger.error(f"[{self.client_name}] Chat loop error: {e}")
                print(f"Error: {e}")

    async def cleanup(self):
        logger.info(f"[{self.client_name}] Cleaning up connection")
        await self.exit_stack.aclose()
