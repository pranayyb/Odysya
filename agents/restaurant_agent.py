import asyncio
import logging
from langchain.tools import StructuredTool
from models.restaurant import Restaurants
from tools.restaurant_tools import RestaurantTools
from config import llm_model

logger = logging.getLogger("RestaurantAgent")


class RestaurantAgent:
    def __init__(self):
        self.tools_client = RestaurantTools()
        self.llm_structured = llm_model.with_structured_output(Restaurants)
        self.search_restaurants_tool = self._create_structured_tool()

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.search_restaurants,
            name="search_restaurants",
            description="Search for restaurants. Accepts a single prompt string; client handles extraction.",
        )

    async def search_restaurants(self, prompt: str) -> str:
        try:
            return await self.tools_client.run(prompt)
        except Exception as e:
            logger.error(f"Error in restaurant search: {e}")
            return f"Error: {e}"

    async def search_and_format(self, query: str) -> Restaurants:
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
            return response
        except Exception as e:
            logger.error(f"Error in search_and_format: {e}")
            return Restaurants(
                success=False,
                restaurants=[],
                notes=f"Error occurred during search: {str(e)}",
            )

    def get_tool(self) -> StructuredTool:
        return self.search_restaurants_tool


if __name__ == "__main__":
    restaurant_agent = RestaurantAgent()
    query = "restaurants in delhi under 20000"
    response = asyncio.run(restaurant_agent.search_and_format(query))
    print(response.model_dump())
