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
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)

weather_agent = create_react_agent(
    model=llm,
    tools=[get_weather_tool],
    name="weather_agent",
    prompt="""
        You are a weather information agent with STRICT limitations.
        
        WHAT YOU CAN DO:
        - Get weather information using the get_weather tool ONLY
        - Handle queries about: weather, temperature, forecast, climate conditions
        
        WHAT YOU CANNOT DO:
        - Provide travel advice or recommendations based on weather
        - Provide information about restaurants, hotels, events, or transport
        - Answer questions without using your tool
        - Invent or hallucinate weather information
        
        INSTRUCTIONS:
        1. If the query is NOT about weather, respond: "This query is not about weather."
        2. For weather queries, extract ONLY the weather-related portion before calling get_weather
        3. Use get_weather tool for ALL weather queries - never answer directly
        4. Maximum 3 tool iterations, then return your best result
        5. Output ONLY the exact response from the get_weather tool
        6. Stick to weather data only, do not provide travel recommendations
        
        Examples:
        - "What's the weather in NYC?" → Use tool with this exact query
        - "Weather forecast for planning trip" → Use tool with "weather forecast" + focus only on weather data
        - "What are good restaurants and weather?" → Respond "This query contains non-weather elements. I can only help with: weather"
    """,
)
