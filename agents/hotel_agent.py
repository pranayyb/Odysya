import asyncio
from models.hotel import Hotels
from tools.hotel_tools import HotelTools
from langchain.tools import StructuredTool
from config import llm_model

tools_client = HotelTools()


def search_hotels(prompt: str):
    return asyncio.run(tools_client.run(prompt))


search_hotels_tool = StructuredTool.from_function(
    func=search_hotels,
    name="search_hotels",
    description="Search for hotels. Accepts a single prompt string; client handles extraction.",
)


llm_structured = llm_model.with_structured_output(Hotels)
query = "hotels in delhi under 20000"

tool_output = search_hotels(query)

response = llm_structured.invoke(
    [
        {
            "role": "system",
            "content": "You are an assistant. Format the following tool output as Hotels JSON.",
        },
        {"role": "user", "content": tool_output},
    ]
)

print(response.model_dump())
