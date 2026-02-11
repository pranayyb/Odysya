import asyncio
from langchain.tools import StructuredTool
from models.attraction import Attractions
from tools.attraction_tools import AttractionTools
from config import llm_model
from utils.logger import get_logger
from utils.error_handler import AgentError

logger = get_logger("AttractionAgent")


class AttractionAgent:
    def __init__(self):
        self.tools_client = AttractionTools()
        self.llm_structured = llm_model.with_structured_output(Attractions)
        self.search_attractions_tool = self._create_structured_tool()
        logger.info("AttractionAgent initialized")

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.search_attractions,
            name="search_attractions",
            description="Search for tourist attractions, monuments, temples, beaches, parks, and museums based on a prompt string.",
        )

    async def search_attractions(self, prompt: str) -> str:
        logger.info(f"AttractionAgent.search_attractions | prompt={prompt[:80]}...")
        try:
            result = await self.tools_client.run(prompt)
            logger.info("AttractionAgent.search_attractions completed")
            return result
        except Exception as e:
            logger.error(f"AttractionAgent.search_attractions failed | error={e}")
            raise AgentError(str(e), agent_name="AttractionAgent")

    async def search_and_format(self, query: str) -> Attractions:
        logger.info(f"AttractionAgent.search_and_format | query={query[:80]}...")
        try:
            tool_output = await self.search_attractions(query)
            response = self.llm_structured.invoke(
                [
                    {
                        "role": "system",
                        "content": "You are an assistant. Format the following tool output as Attractions JSON.",
                    },
                    {"role": "user", "content": tool_output},
                ]
            )
            logger.info(
                f"AttractionAgent.search_and_format completed | success={response.success if hasattr(response, 'success') else True}"
            )
            return response
        except Exception as e:
            logger.error(f"AttractionAgent.search_and_format failed | error={e}")
            raise AgentError(str(e), agent_name="AttractionAgent")

    def get_tool(self) -> StructuredTool:
        return self.search_attractions_tool


if __name__ == "__main__":
    attraction_agent = AttractionAgent()
    query = "tourist attractions in jaipur"
    response = asyncio.run(attraction_agent.search_and_format(query))
    print(response.model_dump())
