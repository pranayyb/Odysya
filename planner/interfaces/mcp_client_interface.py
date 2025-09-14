import asyncio
import json
import logging
import os
from typing import Optional, List, Dict
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from groq import Groq
from config import model_name

from dotenv import load_dotenv

load_dotenv()


class MCPClient:
    """
    unified interface for all mcp clients.
    """

    def __init__(self, api_key_env: str = "GROQ_API_KEY"):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.groq = Groq(api_key=os.environ.get(api_key_env))
        self.tools: List = []
        self.client_name = "Generic"

    async def connect(self, server_script_path: str):
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

        logging.info(f"\nConnected to {self.client_name} server with tools:")
        for tool in self.tools:
            logging.info(f"- {tool.name}: {tool.description}")

    async def process_query(self, query: str) -> str:
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
            model=model_name,
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

                output.append(f"[Calling {tool_name} with {tool_args}]")

                result = await self.session.call_tool(tool_name, tool_args)

                tool_result = result.content[0].text if result.content else str(result)
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
                model=model_name,
            )
            if followup.choices[0].message.content:
                output.append(followup.choices[0].message.content)

        return "\n".join(output)

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
                print(f"Error: {e}")

    async def cleanup(self):
        await self.exit_stack.aclose()
