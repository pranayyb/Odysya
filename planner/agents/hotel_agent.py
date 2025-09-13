import asyncio
import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools.hotel_tools import HotelTools
from langchain.tools import StructuredTool

tools_client = HotelTools()


def search_hotels(prompt: str):
    return asyncio.run(tools_client.run(prompt))


search_hotels_tool = StructuredTool.from_function(
    func=search_hotels,
    name="search_hotels",
    description="Search for hotels. Accepts a single prompt string; client handles extraction.",
)

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
)

hotel_agent = create_react_agent(
    model=llm,
    tools=[search_hotels_tool],
    name="hotel_agent",
    prompt=f"""
        You are the **hotel agent** with STRICT limitations.

        ✅ AVAILABLE TOOL:
        - search_hotels: {search_hotels_tool.description}

        ✅ WHAT YOU CAN DO:
        - Handle queries ONLY about hotels, accommodations, lodging, or stays.
        - Always call the `search_hotels` tool to answer hotel queries.

        🚫 WHAT YOU CANNOT DO:
        - Never invent or call any tool except `search_hotels`.
        - Never call or mention `transfer_to_*` functions (they do not exist).
        - Never provide info about restaurants, events, weather, or transport.
        - Never answer directly without using your tool.

        📋 INSTRUCTIONS:
        1. If the query is NOT about hotels, respond: "This query is not about hotels."
        2. If the query is about hotels, extract ONLY the hotel-related portion and call `search_hotels`.
        3. Maximum of 3 tool calls; after that, return the last tool output.
        4. Output must strictly be the tool’s response.
    """,
)
