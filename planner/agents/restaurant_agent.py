import asyncio
import os
from langchain_groq import ChatGroq
from langchain.tools import StructuredTool
from langgraph.prebuilt import create_react_agent
from tools.restaurant_tools import RestaurantTools

tools_client = RestaurantTools()


def search_restaurants(prompt: str) -> str:
    return asyncio.run(tools_client.run(prompt))


search_restaurants_tool = StructuredTool.from_function(
    func=search_restaurants,
    name="search_restaurants",
    description="Search for restaurants. Accepts a single prompt string; client handles extraction.",
)

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
)

restaurant_agent = create_react_agent(
    model=llm,
    tools=[search_restaurants_tool],
    name="restaurant_agent",
    prompt=f"""
        You are the **restaurant agent** with STRICT limitations.

        ✅ AVAILABLE TOOL:
        - search_restaurants: {search_restaurants_tool.description}

        ✅ WHAT YOU CAN DO:
        - Handle queries ONLY about restaurants, dining, food places, cafes, or bars.
        - Always call the `search_restaurants` tool to answer restaurant queries.

        🚫 WHAT YOU CANNOT DO:
        - Never invent or call any tool except `search_restaurants`.
        - Never call or mention `transfer_to_*` functions (they do not exist).
        - Never provide info about hotels, events, weather, or transport.
        - Never answer directly without using your tool.

        📋 INSTRUCTIONS:
        1. If the query is NOT about restaurants/dining, respond: "This query is not about restaurants."
        2. If the query is about restaurants, extract ONLY the restaurant-related portion and call `search_restaurants`.
        3. Maximum of 3 tool calls; after that, return the last tool output.
        4. Output must strictly be the tool’s response.
    """,
)
