import asyncio
import logging
from langchain.tools import StructuredTool
from models.hotel import Hotels
from tools.hotel_tools import HotelTools
from config import llm_model

logger = logging.getLogger("HotelAgent")


class HotelAgent:
    def __init__(self):
        self.tools_client = HotelTools()
        self.llm_structured = llm_model.with_structured_output(Hotels)
        self.search_hotels_tool = self._create_structured_tool()

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.search_hotels,
            name="search_hotels",
            description="Search for hotels. Accepts a single prompt string; client handles extraction.",
        )

    async def search_hotels(self, prompt: str) -> str:
        try:
            return await self.tools_client.run(prompt)
        except Exception as e:
            logger.error(f"Error in hotel search: {e}")
            return f"Error: {e}"

    async def search_and_format(self, query: str) -> Hotels:
        try:
            tool_output = await self.search_hotels(query)
            response = self.llm_structured.invoke(
                [
                    {
                        "role": "system",
                        "content": "You are an assistant. Format the following tool output as Hotels JSON.",
                    },
                    {"role": "user", "content": tool_output},
                ]
            )
            return response
        except Exception as e:
            logger.error(f"Error in search_and_format: {e}")
            return Hotels(
                success=False,
                hotels=[],
                notes=f"Error occurred during search: {str(e)}",
            )

    def get_tool(self) -> StructuredTool:
        return self.search_hotels_tool


if __name__ == "__main__":
    hotel_agent = HotelAgent()
    query = "hotels in delhi under 20000"
    response = asyncio.run(hotel_agent.search_and_format(query))
    print(response.model_dump())
