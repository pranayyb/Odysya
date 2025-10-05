import asyncio
import os
from langchain_groq import ChatGroq
from langchain.tools import StructuredTool
from langgraph.prebuilt import create_react_agent
from models.restaurant import Restaurants
from tools.restaurant_tools import RestaurantTools
from config import llm_model

tools_client = RestaurantTools()


def search_restaurants(prompt: str) -> str:
    return asyncio.run(tools_client.run(prompt))


search_restaurants_tool = StructuredTool.from_function(
    func=search_restaurants,
    name="search_restaurants",
    description="Search for restaurants. Accepts a single prompt string; client handles extraction.",
)

llm_structured = llm_model.with_structured_output(Restaurants)
query = "restaurants in delhi under 20000"

tool_output = search_restaurants(query)

response = llm_structured.invoke(
    [
        {
            "role": "system",
            "content": "You are an assistant. Format the following tool output as Restaurants JSON.",
        },
        {"role": "user", "content": tool_output},
    ]
)

print(response.model_dump())
