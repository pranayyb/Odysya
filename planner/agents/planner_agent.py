import os
from dotenv import load_dotenv
from agents.restaurant_agent import restaurant_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

from langchain_core.messages import convert_to_messages


def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")


from langgraph_supervisor import create_supervisor


gemini_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # or "gemini-1.5-pro"
    google_api_key=os.getenv("GEMINI_API_KEY"),
)
# print(gemini_model.invoke("whats up?").content)


supervisor = create_supervisor(
    model=gemini_model,
    agents=[restaurant_agent],
    prompt=(
        """You are a supervisor managing one agent:
        - restaurant_agent: The agent is a restaurant agent.
        - You must delegate all restaurant queries to the agent.
        - Do not generate or invent any restaurants yourself.
        - Only output the result provided by the agent.

        """
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile()


for chunk in supervisor.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "provide restaurants in Tokyo",
            }
        ]
    },
):
    pretty_print_messages(chunk, last_message=True)


final_message_history = chunk["supervisor"]["messages"]
print("=== Final Answer ===")
print("Final Answer:", final_message_history[-1].content)
