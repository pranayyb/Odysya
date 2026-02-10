import asyncio
from langchain.tools import StructuredTool
from models.hotel import Hotels
from tools.hotel_tools import HotelTools
from config import llm_model
from utils.logger import get_logger
from utils.error_handler import AgentError

logger = get_logger("HotelAgent")


class HotelAgent:
    def __init__(self):
        self.tools_client = HotelTools()
        self.llm_structured = llm_model.with_structured_output(Hotels)
        self.search_hotels_tool = self._create_structured_tool()
        logger.info("HotelAgent initialized")

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.search_hotels,
            name="search_hotels",
            description="Search for hotels. Accepts a single prompt string; client handles extraction.",
        )

    async def search_hotels(self, prompt: str) -> str:
        logger.info(f"HotelAgent.search_hotels | prompt={prompt[:80]}...")
        try:
            result = await self.tools_client.run(prompt)
            logger.info("HotelAgent.search_hotels completed")
            return result
        except Exception as e:
            logger.error(f"HotelAgent.search_hotels failed | error={e}")
            raise AgentError(str(e), agent_name="HotelAgent")

    async def search_and_format(self, query: str) -> Hotels:
        logger.info(f"HotelAgent.search_and_format | query={query[:80]}...")
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
            logger.info(
                f"HotelAgent.search_and_format completed | success={response.success if hasattr(response, 'success') else True}"
            )
            return response
        except Exception as e:
            logger.error(f"HotelAgent.search_and_format failed | error={e}")
            raise AgentError(str(e), agent_name="HotelAgent")

    def get_tool(self) -> StructuredTool:
        return self.search_hotels_tool


if __name__ == "__main__":
    hotel_agent = HotelAgent()
    query = "hotels in delhi under 20000"
    response = asyncio.run(hotel_agent.search_and_format(query))
    print(response.model_dump())
