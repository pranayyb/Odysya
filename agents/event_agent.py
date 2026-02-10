import asyncio
from langchain.tools import StructuredTool
from models.event import Events
from tools.event_tools import EventTools
from config import llm_model
from utils.logger import get_logger
from utils.error_handler import AgentError

logger = get_logger("EventAgent")


class EventAgent:
    def __init__(self):
        self.tools_client = EventTools()
        self.llm_structured = llm_model.with_structured_output(Events)
        self.search_events_tool = self._create_structured_tool()
        logger.info("EventAgent initialized")

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.search_events,
            name="search_events",
            description="Search for events, concerts, shows, festivals, or entertainment based on a prompt string.",
        )

    async def search_events(self, prompt: str) -> str:
        logger.info(f"EventAgent.search_events | prompt={prompt[:80]}...")
        try:
            result = await self.tools_client.run(prompt)
            logger.info("EventAgent.search_events completed")
            return result
        except Exception as e:
            logger.error(f"EventAgent.search_events failed | error={e}")
            raise AgentError(str(e), agent_name="EventAgent")

    async def search_and_format(self, query: str) -> Events:
        logger.info(f"EventAgent.search_and_format | query={query[:80]}...")
        try:
            tool_output = await self.search_events(query)
            response = self.llm_structured.invoke(
                [
                    {
                        "role": "system",
                        "content": "You are an assistant. Format the following tool output as Events JSON.",
                    },
                    {"role": "user", "content": tool_output},
                ]
            )
            logger.info(
                f"EventAgent.search_and_format completed | success={response.success if hasattr(response, 'success') else True}"
            )
            return response
        except Exception as e:
            logger.error(f"EventAgent.search_and_format failed | error={e}")
            raise AgentError(str(e), agent_name="EventAgent")

    def get_tool(self) -> StructuredTool:
        return self.search_events_tool


if __name__ == "__main__":
    event_agent = EventAgent()
    query = "events happening in mumbai"
    response = asyncio.run(event_agent.search_and_format(query))
    print(response.model_dump())
