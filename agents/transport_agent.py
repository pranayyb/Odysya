import asyncio
import logging
from langchain.tools import StructuredTool
from models.transport import Transport
from tools.transport_tools import TransportTools
from config import llm_model

logger = logging.getLogger("TransportAgent")


class TransportAgent:
    def __init__(self):
        self.tools_client = TransportTools()
        self.llm_structured = llm_model.with_structured_output(Transport)
        self.search_transports_tool = self._create_structured_tool()

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.search_transports,
            name="search_transports",
            description="Search for transport options. Accepts a single prompt string; client handles extraction.",
        )

    async def search_transports(self, prompt: str) -> str:
        try:
            return await self.tools_client.run(prompt)
        except Exception as e:
            logger.error(f"Error in transport search: {e}")
            return f"Error: {e}"

    async def search_and_format(self, query: str) -> Transport:
        try:
            tool_output = await self.search_transports(query)
            response = self.llm_structured.invoke(
                [
                    {
                        "role": "system",
                        "content": "You are an assistant. Format the following tool output as Transport JSON.",
                    },
                    {"role": "user", "content": tool_output},
                ]
            )
            return response
        except Exception as e:
            logger.error(f"Error in search_and_format: {e}")
            return Transport(
                success=False,
                transport=[],
                notes=f"Error occurred during search: {str(e)}",
            )

    def get_tool(self) -> StructuredTool:
        return self.search_transports_tool


if __name__ == "__main__":
    transport_agent = TransportAgent()
    query = "transport options to delhi from mumbai"
    response = asyncio.run(transport_agent.search_and_format(query))
    print(response.model_dump())
