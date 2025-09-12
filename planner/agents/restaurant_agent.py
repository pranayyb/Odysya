import asyncio
import os
from typing import Optional
from langchain_groq import ChatGroq
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from langgraph.prebuilt import create_react_agent
from tools.restaurant_tools import RestaurantTools

tools_client = RestaurantTools()


class SearchRestaurantsInput(BaseModel):
    location: str = Field(..., description="The city or area to search restaurants in")


def search_restaurants(location: str, term: Optional[str] = None) -> str:
    return asyncio.run(tools_client.run(f"search restaurants in {location}"))


search_restaurants_tool = StructuredTool.from_function(
    func=search_restaurants,
    name="search_restaurants",
    description="Search for restaurants",
    args_schema=SearchRestaurantsInput,
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)

restaurant_agent = create_react_agent(
    model=llm,
    tools=[search_restaurants_tool],
    name="restaurant_agent",
    prompt="""
        You are a restaurant agent. You **cannot** answer any question yourself.
        Also keep max iteration to 3 after that output whatever the result you have.
        You **must** always call the search_restaurants tool to answer queries.
        Do not hallucinate, do not invent restaurants, do not provide any information not returned by the tool.
        Your output must strictly be the tool’s response only.
        """,
)
