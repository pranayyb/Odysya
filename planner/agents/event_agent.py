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
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
)

event_agent = create_react_agent(
    model=llm,
    tools=[search_events_tool],
    name="event_agent",
    prompt=f"""
        You are the **event agent** with STRICT limitations.

        ✅ AVAILABLE TOOL:
        - search_events: {search_events_tool.description}

        ✅ WHAT YOU CAN DO:
        - Handle queries ONLY about events, concerts, shows, festivals, or entertainment.
        - Always call the `search_events` tool to answer event queries.

        🚫 WHAT YOU CANNOT DO:
        - Never invent or call any tool except `search_events`.
        - Never call or mention `transfer_to_*` functions (they do not exist).
        - Never provide info about hotels, restaurants, weather, or transport.
        - Never answer directly without using your tool.

        📋 INSTRUCTIONS:
        1. If the query is NOT about events, respond: "This query is not about events."
        2. If the query is about events, extract ONLY the event-related portion and call `search_events`.
        3. Maximum of 3 tool calls; after that, return the last tool output.
        4. Output must strictly be the tool’s response.
    """,
)
