import asyncio
import logging
from langchain.tools import StructuredTool
from models.event import Events
from tools.event_tools import EventTools
from config import llm_model

logger = logging.getLogger("EventAgent")


class EventAgent:
    def __init__(self):
        self.tools_client = EventTools()
        self.llm_structured = llm_model.with_structured_output(Events)
        self.search_events_tool = self._create_structured_tool()

    def _create_structured_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.search_events,
            name="search_events",
            description="Search for events, concerts, shows, festivals, or entertainment based on a prompt string.",
        )

    async def search_events(self, prompt: str) -> str:
        try:
            return await self.tools_client.run(prompt)
        except Exception as e:
            logger.error(f"Error in event search: {e}")
            return f"Error: {e}"

    async def search_and_format(self, query: str) -> Events:
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
            return response
        except Exception as e:
            logger.error(f"Error in search_and_format: {e}")
            return Events(
                success=False,
                events=[],
                notes=f"Error occurred during search: {str(e)}",
            )

    def get_tool(self) -> StructuredTool:
        return self.search_events_tool


if __name__ == "__main__":
    event_agent = EventAgent()
    query = "events happening in mumbai"
    response = asyncio.run(event_agent.search_and_format(query))
    print(response.model_dump())
