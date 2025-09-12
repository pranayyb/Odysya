import asyncio
from typing import TypedDict, List, Optional
from langchain.tools import Tool
from langchain_groq import ChatGroq
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate


class EventState(TypedDict):
    query: str
    thoughts: List[str]
    tool_calls: List[str]
    results: Optional[List[str]]
    final_answer: Optional[str]


from tools.event_tools import EventTools

tools_client = EventTools()

tools = [
    Tool(
        name="search_event",
        description="Search for event information in a given city",
        func=lambda city: asyncio.run(tools_client.run(f"search events in {city}")),
    ),
]

llm = ChatGroq(model="llama-3.1-8b-instant")

react_prompt = hub.pull("hwchase17/react")

final_answer_instruction = """
You are an agent that can call tools to help answer the user's query.
Once you have enough information, or if you cannot use more tools, you MUST provide a final answer.
Always format it exactly like: Final Answer: <your answer here>
Do not keep reasoning endlessly.
"""

modified_prompt = PromptTemplate(
    template=final_answer_instruction + react_prompt.template,
    input_variables=react_prompt.input_variables,
)

event_agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=modified_prompt,
)

event_executor = AgentExecutor.from_agent_and_tools(
    agent=event_agent,
    tools=tools,
    verbose=True,
    max_iterations=3,
    return_intermediate_steps=True,
)


async def event_node(state: EventState) -> EventState:
    query = state["query"]

    result = await event_executor.ainvoke({"input": query})

    if result.get("output") and "stopped" not in result["output"].lower():
        final_output = result["output"]
    elif result.get("intermediate_steps"):
        last_step = result["intermediate_steps"][-1]
        action, observation = last_step
        final_output = observation
    else:
        final_output = "No output generated."

    return {
        "query": query,
        "thoughts": state.get("thoughts", []) + [str(result)],
        "tool_calls": state.get("tool_calls", []),
        "results": [final_output],
        "final_answer": final_output,
    }


# example  run
if __name__ == "__main__":

    async def test():
        init_state: EventState = {
            "query": "events in london",
            "thoughts": [],
            "tool_calls": [],
            "results": None,
            "final_answer": None,
        }

        new_state = await weather_node(init_state)
        print("=== Final Answer ===")
        print("Final Answer:", new_state["final_answer"])

    asyncio.run(test())
