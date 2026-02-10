import asyncio
from langchain.tools import StructuredTool
from models.restaurant import Restaurants
from tools.restaurant_tools import RestaurantTools
from config import llm_model
from utils.logger import get_logger
from utils.error_handler import AgentError

logger = get_logger("RestaurantAgent")


class RestaurantAgent:
    def __init__(self):
        self.tools_client = RestaurantTools()
        self.llm_structured = llm_model.with_structured_output(Restaurants)
        self.search_restaurants_tool = self._create_structured_tool()
        logger.info("RestaurantAgent initialized")

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.search_restaurants,
            name="search_restaurants",
            description="Search for restaurants. Accepts a single prompt string; client handles extraction.",
        )

    async def search_restaurants(self, prompt: str) -> str:
        logger.info(f"RestaurantAgent.search_restaurants | prompt={prompt[:80]}...")
        try:
            result = await self.tools_client.run(prompt)
            logger.info("RestaurantAgent.search_restaurants completed")
            return result
        except Exception as e:
            logger.error(f"RestaurantAgent.search_restaurants failed | error={e}")
            raise AgentError(str(e), agent_name="RestaurantAgent")

    async def search_and_format(self, query: str) -> Restaurants:
        logger.info(f"RestaurantAgent.search_and_format | query={query[:80]}...")
        try:
            tool_output = await self.search_restaurants(query)
            response = self.llm_structured.invoke(
                [
                    {
                        "role": "system",
                        "content": "You are an assistant. Format the following tool output as Restaurants JSON.",
                    },
                    {"role": "user", "content": tool_output},
                ]
            )
            logger.info(
                f"RestaurantAgent.search_and_format completed | success={response.success if hasattr(response, 'success') else True}"
            )
            return response
        except Exception as e:
            logger.error(f"RestaurantAgent.search_and_format failed | error={e}")
            raise AgentError(str(e), agent_name="RestaurantAgent")

    def get_tool(self) -> StructuredTool:
        return self.search_restaurants_tool


if __name__ == "__main__":
    restaurant_agent = RestaurantAgent()
    query = "restaurants in delhi under 20000"
    response = asyncio.run(restaurant_agent.search_and_format(query))
    print(response.model_dump())
