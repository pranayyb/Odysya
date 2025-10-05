import asyncio
import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from models.weather import Weather
from tools.weather_tools import WeatherTools
from langchain.tools import StructuredTool
from config import llm_model

tools_client = WeatherTools()


def get_weather(prompt: str) -> str:
    return asyncio.run(tools_client.run(prompt))


get_weather_tool = StructuredTool.from_function(
    func=get_weather,
    name="get_weather",
    description="Get the current weather for a given location. Accepts a single prompt string; client handles extraction.",
)

llm_structured = llm_model.with_structured_output(Weather)
query = "current weather in mumbai"

tool_output = get_weather(query)

response = llm_structured.invoke(
    [
        {
            "role": "system",
            "content": "You are an assistant. Format the following tool output as Weather JSON.",
        },
        {"role": "user", "content": tool_output},
    ]
)

print(response.model_dump())
