import asyncio
import logging
from langchain.tools import StructuredTool
from models.weather import Weather
from tools.weather_tools import WeatherTools
from config import llm_model

logger = logging.getLogger("WeatherAgent")


class WeatherAgent:
    def __init__(self):
        self.tools_client = WeatherTools()
        self.llm_structured = llm_model.with_structured_output(Weather)
        self.get_weather_tool = self._create_structured_tool()

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.get_weather,
            name="get_weather",
            description="Get the current weather for a given location. Accepts a single prompt string; client handles extraction.",
        )

    async def get_weather(self, prompt: str) -> str:
        try:
            return await self.tools_client.run(prompt)
        except Exception as e:
            logger.error(f"Error in weather retrieval: {e}")
            return f"Error: {e}"

    async def search_and_format(self, query: str) -> Weather:
        try:
            tool_output = await self.get_weather(query)
            response = self.llm_structured.invoke(
                [
                    {
                        "role": "system",
                        "content": "You are an assistant. Format the following tool output as Weather JSON.",
                    },
                    {"role": "user", "content": tool_output},
                ]
            )
            return response
        except Exception as e:
            logger.error(f"Error in search_and_format: {e}")
            return Weather(
                success=False,
                weather=[],
                notes=f"Error occurred during weather retrieval: {str(e)}",
            )

    def get_tool(self) -> StructuredTool:
        return self.get_weather_tool


if __name__ == "__main__":
    weather_agent = WeatherAgent()
    query = "current weather in mumbai"
    response = asyncio.run(weather_agent.search_and_format(query))
    print(response.model_dump())
