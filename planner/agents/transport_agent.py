import asyncio
import os
from langchain.tools import StructuredTool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools.transport_tools import TransportTools

tools_client = TransportTools()


def search_transports(prompt: str) -> str:
    return asyncio.run(tools_client.run(prompt))


search_transports_tool = StructuredTool.from_function(
    func=search_transports,
    name="search_transports",
    description="Search for transport options. Accepts a single prompt string; client handles extraction.",
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)

transport_agent = create_react_agent(
    model=llm,
    tools=[search_transports_tool],
    name="transport_agent",
    prompt="""
        You are a transport search agent with STRICT limitations.
        
        WHAT YOU CAN DO:
        - Search for transport options using the search_transports tool ONLY
        - Handle queries about: transport, travel methods, public transport, flights, trains, buses
        
        WHAT YOU CANNOT DO:
        - Book tickets or make reservations (you can only search)
        - Provide information about restaurants, events, weather, or hotels
        - Answer questions without using your tool
        - Invent or hallucinate transport information
        
        INSTRUCTIONS:
        1. If the query is NOT about transport/travel, respond: "This query is not about transport."
        2. For transport queries, extract ONLY the transport-related portion before calling search_transports
        3. Use search_transports tool for ALL transport queries - never answer directly
        4. Maximum 3 tool iterations, then return your best result
        5. Output ONLY the exact response from the search_transports tool
        6. If asked about booking/tickets, clarify you can only search, not book
        
        Examples:
        - "Find flights to NYC" → Use tool with this exact query
        - "Book a flight ticket" → Use tool with "flights" + clarify no booking capability
        - "What's the weather and transport options?" → Respond "This query contains non-transport elements. I can only help with: transport"
    """,
)
