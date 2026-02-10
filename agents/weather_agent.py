import asyncio
from langchain.tools import StructuredTool
from models.weather import Weather
from tools.weather_tools import WeatherTools
from config import llm_model
from utils.logger import get_logger
from utils.error_handler import AgentError

logger = get_logger("WeatherAgent")


class WeatherAgent:
    def __init__(self):
        self.tools_client = WeatherTools()
        self.llm_structured = llm_model.with_structured_output(Weather)
        self.get_weather_tool = self._create_structured_tool()
        logger.info("WeatherAgent initialized")

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.get_weather,
            name="get_weather",
            description="Get the current weather for a given location. Accepts a single prompt string; client handles extraction.",
        )

    async def get_weather(self, prompt: str) -> str:
        logger.info(f"WeatherAgent.get_weather | prompt={prompt[:80]}...")
        try:
            result = await self.tools_client.run(prompt)
            logger.info("WeatherAgent.get_weather completed")
            return result
        except Exception as e:
            logger.error(f"WeatherAgent.get_weather failed | error={e}")
            raise AgentError(str(e), agent_name="WeatherAgent")

    async def search_and_format(self, query: str) -> Weather:
        logger.info(f"WeatherAgent.search_and_format | query={query[:80]}...")
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
            logger.info(
                f"WeatherAgent.search_and_format completed | success={response.success if hasattr(response, 'success') else True}"
            )
            return response
        except Exception as e:
            logger.error(f"WeatherAgent.search_and_format failed | error={e}")
            raise AgentError(str(e), agent_name="WeatherAgent")

    def get_tool(self) -> StructuredTool:
        return self.get_weather_tool


if __name__ == "__main__":
    weather_agent = WeatherAgent()
    query = "current weather in mumbai"
    response = asyncio.run(weather_agent.search_and_format(query))
    print(response.model_dump())
