import asyncio
from langchain.tools import StructuredTool
from models.event import Events
from tools.event_tools import EventTools
from config import llm_model


tools_client = EventTools()


def search_events(prompt: str) -> str:
    """Wrapper to run event search asynchronously."""
    return asyncio.run(tools_client.run(prompt))


search_events_tool = StructuredTool.from_function(
    func=search_events,
    name="search_events",
    description="Search for events, concerts, shows, festivals, or entertainment based on a prompt string.",
)


llm_structured = llm_model.with_structured_output(Events)
query = "events happening in mumbai"

tool_output = search_events(query)

response = llm_structured.invoke(
    [
        {
            "role": "system",
            "content": "You are an assistant. Format the following tool output as Events JSON.",
        },
        {"role": "user", "content": tool_output},
    ]
)

print(response.model_dump())
