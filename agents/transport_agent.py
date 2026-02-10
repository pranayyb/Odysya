import asyncio
from langchain.tools import StructuredTool
from models.transport import Transport
from tools.transport_tools import TransportTools
from config import llm_model
from utils.logger import get_logger
from utils.error_handler import AgentError

logger = get_logger("TransportAgent")


class TransportAgent:
    def __init__(self):
        self.tools_client = TransportTools()
        self.llm_structured = llm_model.with_structured_output(Transport)
        self.search_transports_tool = self._create_structured_tool()
        logger.info("TransportAgent initialized")

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.search_transports,
            name="search_transports",
            description="Search for transport options. Accepts a single prompt string; client handles extraction.",
        )

    async def search_transports(self, prompt: str) -> str:
        logger.info(f"TransportAgent.search_transports | prompt={prompt[:80]}...")
        try:
            result = await self.tools_client.run(prompt)
            logger.info("TransportAgent.search_transports completed")
            return result
        except Exception as e:
            logger.error(f"TransportAgent.search_transports failed | error={e}")
            raise AgentError(str(e), agent_name="TransportAgent")

    async def search_and_format(self, query: str) -> Transport:
        logger.info(f"TransportAgent.search_and_format | query={query[:80]}...")
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
            logger.info(
                f"TransportAgent.search_and_format completed | success={response.success if hasattr(response, 'success') else True}"
            )
            return response
        except Exception as e:
            logger.error(f"TransportAgent.search_and_format failed | error={e}")
            raise AgentError(str(e), agent_name="TransportAgent")

    def get_tool(self) -> StructuredTool:
        return self.search_transports_tool


if __name__ == "__main__":
    transport_agent = TransportAgent()
    query = "transport options to delhi from mumbai"
    response = asyncio.run(transport_agent.search_and_format(query))
    print(response.model_dump())
