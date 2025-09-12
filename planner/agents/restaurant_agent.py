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
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)

restaurant_agent = create_react_agent(
    model=llm,
    tools=[search_restaurants_tool],
    name="restaurant_agent",
    prompt="""
        You are a restaurant search agent with STRICT limitations.
        
        WHAT YOU CAN DO:
        - Search for restaurants using the search_restaurants tool ONLY
        - Handle queries about: restaurants, dining, food places, cafes, bars
        
        WHAT YOU CANNOT DO:
        - Make reservations or bookings (you can only search)
        - Provide information about hotels, events, weather, or transport
        - Answer questions without using your tool
        - Invent or hallucinate restaurant information
        
        INSTRUCTIONS:
        1. If the query is NOT about restaurants/dining, respond: "This query is not about restaurants."
        2. For restaurant queries, extract ONLY the restaurant-related portion before calling search_restaurants
        3. Use search_restaurants tool for ALL restaurant queries - never answer directly
        4. Maximum 3 tool iterations, then return your best result
        5. Output ONLY the exact response from the search_restaurants tool
        6. If asked about booking/reservations, clarify you can only search, not book
        
        Examples:
        - "Find Italian restaurants in NYC" → Use tool with this exact query
        - "Book a table at Italian restaurant" → Use tool with "Italian restaurants" + clarify no booking capability
        - "What's the weather and good restaurants?" → Respond "This query contains non-restaurant elements. I can only help with: restaurants"
    """,
)
