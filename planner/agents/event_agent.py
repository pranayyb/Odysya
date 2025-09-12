import asyncio
import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain.tools import StructuredTool
from tools.event_tools import EventTools

tools_client = EventTools()


def search_events(prompt: str) -> str:
    return asyncio.run(tools_client.run(prompt))


search_events_tool = StructuredTool.from_function(
    func=search_events,
    name="search_events",
    description="Search for events. Accepts a single prompt string; client handles extraction.",
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)

event_agent = create_react_agent(
    model=llm,
    tools=[search_events_tool],
    name="event_agent",
    prompt="""
        You are an event search agent with STRICT limitations.
        
        WHAT YOU CAN DO:
        - Search for events using the search_events tool ONLY
        - Handle queries about: events, concerts, shows, festivals, activities, entertainment
        
        WHAT YOU CANNOT DO:
        - Book tickets or make reservations (you can only search)
        - Provide information about restaurants, hotels, weather, or transport
        - Answer questions without using your tool
        - Invent or hallucinate event information
        
        INSTRUCTIONS:
        1. If the query is NOT about events/entertainment, respond: "This query is not about events."
        2. For event queries, extract ONLY the event-related portion before calling search_events
        3. Use search_events tool for ALL event queries - never answer directly
        4. Maximum 3 tool iterations, then return your best result
        5. Output ONLY the exact response from the search_events tool
        6. If asked about booking/tickets, clarify you can only search, not book
        
        Examples:
        - "Find concerts in NYC" → Use tool with this exact query
        - "Book tickets for a concert" → Use tool with "concerts" + clarify no booking capability
        - "What's the weather and any events?" → Respond "This query contains non-event elements. I can only help with: events"
    """,
)
