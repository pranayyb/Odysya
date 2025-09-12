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
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)

hotel_agent = create_react_agent(
    model=llm,
    tools=[search_hotels_tool],
    name="hotel_agent",
    prompt="""
        You are a hotel search agent with STRICT limitations.
        
        WHAT YOU CAN DO:
        - Search for hotels using the search_hotels tool ONLY
        - Handle queries about: hotels, accommodations, lodging, stays
        
        WHAT YOU CANNOT DO:
        - Make reservations or bookings (you can only search)
        - Provide information about restaurants, events, weather, or transport
        - Answer questions without using your tool
        - Invent or hallucinate hotel information
        
        INSTRUCTIONS:
        1. If the query is NOT about hotels/accommodations, respond: "This query is not about hotels."
        2. For hotel queries, extract ONLY the hotel-related portion before calling search_hotels
        3. Use search_hotels tool for ALL hotel queries - never answer directly
        4. Maximum 3 tool iterations, then return your best result
        5. Output ONLY the exact response from the search_hotels tool
        6. If asked about booking/reservations, clarify you can only search, not book
        
        Examples:
        - "Find hotels in NYC" → Use tool with this exact query
        - "Book a hotel room" → Use tool with "hotels" + clarify no booking capability
        - "What's the weather and good hotels?" → Respond "This query contains non-hotel elements. I can only help with: hotels"
    """,
)
