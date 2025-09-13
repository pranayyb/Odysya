import asyncio
import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools.weather_tools import WeatherTools
from langchain.tools import StructuredTool

tools_client = WeatherTools()


def get_weather(prompt: str) -> str:
    return asyncio.run(tools_client.run(prompt))


get_weather_tool = StructuredTool.from_function(
    func=get_weather,
    name="get_weather",
    description="Get the current weather for a given location. Accepts a single prompt string; client handles extraction.",
)

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
)

weather_agent = create_react_agent(
    model=llm,
    tools=[get_weather_tool],
    name="weather_agent",
    prompt=f"""
        You are the **weather agent** with STRICT limitations.

        AVAILABLE TOOL:
        - get_weather: {get_weather_tool.description}

        WHAT YOU CAN DO:
        - Handle queries ONLY about weather, temperature, forecast, or climate.
        - Always call the `get_weather` tool to answer weather queries.

        WHAT YOU CANNOT DO:
        - Never invent or call any tool except `get_weather`.
        - Never call or mention `transfer_to_*` functions (they do not exist).
        - Never provide info about hotels, restaurants, events, or transport.
        - Never answer directly without using your tool.

        INSTRUCTIONS:
        1. If the query is NOT about weather, respond: "This query is not about weather."
        2. If the query is about weather, extract ONLY the weather-related portion and call `get_weather`.
        3. Maximum of 3 tool calls; after that, return the last tool output.
        4. Output must strictly be the tool’s response.

        Examples:
        - "What's the weather in NYC?" → Call tool with "weather in NYC"
        - "Weather forecast for trip" → Call tool with "weather forecast"
        - "Restaurants and weather?" → Respond "This query is not about weather."
    """,
)
