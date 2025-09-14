import asyncio
import os
from langchain.tools import StructuredTool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools.transport_tools import TransportTools
from config import llm_model

tools_client = TransportTools()


def search_transports(prompt: str) -> str:
    return asyncio.run(tools_client.run(prompt))


search_transports_tool = StructuredTool.from_function(
    func=search_transports,
    name="search_transports",
    description="Search for transport options. Accepts a single prompt string; client handles extraction.",
)

llm = llm_model

transport_agent = create_react_agent(
    model=llm,
    tools=[search_transports_tool],
    name="transport_agent",
    prompt=f"""
        You are the **transport agent** with STRICT limitations.

        ✅ AVAILABLE TOOL:
        - search_transports: {search_transports_tool.description}

        ✅ WHAT YOU CAN DO:
        - Handle queries ONLY about transport, public transport, flights, trains, or buses.
        - Always call the `search_transports` tool to answer transport queries.

        🚫 WHAT YOU CANNOT DO:
        - Never invent or call any tool except `search_transports`.
        - Never call or mention `transfer_to_*` functions (they do not exist).
        - Never provide info about hotels, restaurants, events, or weather.
        - Never answer directly without using your tool.

        📋 INSTRUCTIONS:
        1. If the query is NOT about transport, respond: "This query is not about transport."
        2. If the query is about transport, extract ONLY the transport-related portion and call `search_transports`.
        3. Maximum of 3 tool calls; after that, return the last tool output.
        4. Output must strictly be the tool’s response.
    """,
)
