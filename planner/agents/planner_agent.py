import os
from dotenv import load_dotenv
from agents import *
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from utils.pretty_print import pretty_print_messages
from langchain.schema import AIMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import ToolMessage

load_dotenv()


# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

gemini_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)
# print(gemini_model.invoke("whats up?").content)


# also before processing the user input, i need to check if i have all the details or else make an interrupt to get those details (like human in the loop)
# not implemented yet


supervisor = create_supervisor(
    model=gemini_model,
    agents=[restaurant_agent, event_agent, weather_agent, hotel_agent, transport_agent],
    prompt="""
        You are a routing supervisor. Your ONLY job is to delegate queries to the correct agent(s).

        RULES:
        - Never summarize or produce your own "Final Answer".
        - Never invent or call tools like 'transfer_to_X'. They do not exist.
        - Only route queries to one or more of these agents:
            - restaurant_agent
            - event_agent
            - weather_agent
            - hotel_agent
            - transport_agent
        - Extract only the relevant portion of the query for each agent.
        - If multiple agents are needed, call them sequentially and return their outputs combined as-is.
        - Do NOT rephrase, reword, or summarize agent outputs. Return their raw responses only.
        - If no relevant agent exists, return: "No available agent can handle this request."
    """,
    add_handoff_back_messages=True,
    output_mode="full_history",  # ensures you see every step
).compile()


for chunk in supervisor.stream(
    # {
    #     "messages": [
    #         {
    #             "role": "user",
    #             "content": "provide italian restaurants in new york",
    #         }
    #     ]
    # },
    {
        "messages": [
            {
                "role": "user",
                "content": """
                            I am planning a trip to Delhi. 
                            Can you do the following for me: 
                            1. Find some restaurants in delhi. 
                            2. Suggest any music events happening there. 
                            3. Tell me the weather forecast of the city. 
                            4. Recommend hotels for stay in . 
                            5. Suggest the modes of transport to delhi from mumbai.
                            """,
            }
        ]
    },
):
    if chunk and "messages" in chunk:
        pretty_print_messages(chunk, last_message=True)

data = []
final_message_history = chunk["supervisor"]["messages"]
print("=== Final Answer ===")
# print(final_message_history)
for msg in final_message_history:
    if isinstance(msg, AIMessage):
        data.append(msg.content)
# print("Final Answer:", final_message_history[-1].content)


print(gemini_model.invoke(f"with this data generate an itinerary {data}").content)
