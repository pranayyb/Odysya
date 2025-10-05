import asyncio
import os
from langchain.tools import StructuredTool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from models.transport import Transport
from tools.transport_tools import TransportTools
from config import llm_model

tools_client = TransportTools()


def search_transports(prompt: str) -> str:
    return asyncio.run(tools_client.run(prompt))


search_transports_tool = StructuredTool.from_function(
    func=search_transports,
    name="search_transports",
    description="Search for transport options. Accepts a single prompt string; client handles extraction.",
)

llm_structured = llm_model.with_structured_output(Transport)
query = "transport options to delhi from mumbai"

tool_output = search_transports(query)

response = llm_structured.invoke(
    [
        {
            "role": "system",
            "content": "You are an assistant. Format the following tool output as Transport JSON.",
        },
        {"role": "user", "content": tool_output},
    ]
)

print(response.model_dump())
