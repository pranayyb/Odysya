import json
import os
from typing import Optional, List
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from groq import Groq
from config import MODEL_NAME
from utils.logger import get_logger
from utils.error_handler import ClientError

from dotenv import load_dotenv

load_dotenv()

logger = get_logger("MCPClient")


class MCPClient:
    def __init__(self, api_key_env: str = "GROQ_API_KEY"):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.groq = Groq(api_key=os.environ.get(api_key_env))
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

    async def process_query(self, query: str) -> str:
        logger.info(f"[{self.client_name}] Processing query: {query[:100]}...")
        try:
            messages = [{"role": "user", "content": query}]

            available_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in self.tools
            ]

            response = self.groq.chat.completions.create(
                messages=messages,
                model=MODEL_NAME,
                tools=available_tools,
                tool_choice="auto",
            )

            response_message = response.choices[0].message
            messages.append(response_message)

            output = []

            if response_message.content:
                output.append(response_message.content)

            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}

                    logger.info(
                        f"[{self.client_name}] Calling tool: {tool_name} | args={tool_args}"
                    )

                    result = await self.session.call_tool(tool_name, tool_args)

                    tool_result = (
                        result.content[0].text if result.content else str(result)
                    )
                    logger.info(
                        f"[{self.client_name}] Tool {tool_name} returned {len(tool_result)} chars"
                    )
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": tool_result,
                        }
                    )

                followup = self.groq.chat.completions.create(
                    messages=messages
                    + [
                        {
                            "role": "system",
                            "content": f"Summarize the tool results clearly for the user. "
                            f"Do not invent information beyond what the tool returned. "
                            f"Only simplify and rephrase.",
                        }
                    ],
                    model=MODEL_NAME,
                )
                if followup.choices[0].message.content:
                    output.append(followup.choices[0].message.content)

            logger.info(f"[{self.client_name}] Query processed successfully")
            return "\n".join(output)

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
