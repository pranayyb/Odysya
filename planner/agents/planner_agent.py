import os
from dotenv import load_dotenv
from agents import *
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from utils.pretty_print import pretty_print_messages

load_dotenv()


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

gemini_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # or "gemini-1.5-pro"
    google_api_key=os.getenv("GEMINI_API_KEY"),
)
# print(gemini_model.invoke("whats up?").content)

supervisor = create_supervisor(
    model=gemini_model,
    agents=[restaurant_agent, event_agent, weather_agent, hotel_agent, transport_agent],
    prompt=(
        """
        You are a precise routing supervisor managing specialized agents. Each agent can ONLY handle its specific domain and has limited tools.

        AGENT CAPABILITIES:
        - restaurant_agent: ONLY restaurants, dining, food places. Tool: search_restaurants
        - event_agent: ONLY events, concerts, shows, activities. Tool: search_events  
        - weather_agent: ONLY weather, forecast, temperature. Tool: get_weather
        - hotel_agent: ONLY hotels, accommodations, lodging. Tool: search_hotels
        - transport_agent: ONLY transport, travel methods, public transport. Tool: search_transports

        ROUTING RULES:
        1. Analyze the user query and identify ONLY the specific parts each agent can handle
        2. Extract and send ONLY the relevant portion to each agent (e.g., for "restaurants in Paris", send only "restaurants in Paris" to restaurant_agent)
        3. Do NOT send queries about unavailable services (no booking, no reservations, no detailed planning)
        4. If an agent cannot handle a request, it will respond appropriately
        5. Delegate tasks sequentially, not in parallel
        6. Each agent has exactly one tool - do not expect capabilities beyond their tool scope

        EXAMPLE ROUTING:
        - "Find Italian restaurants and book a table" → restaurant_agent gets "Find Italian restaurants" (ignore booking part)
        - "Weather and hotels in NYC" → weather_agent gets "weather in NYC", hotel_agent gets "hotels in NYC"
        - "Plan my trip" → Break down to specific searchable items only

        Be precise: only route what each agent can actually search for with their available tools.
        """
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
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
                "content":  """
                            I am planning a trip to New York next weekend. 
                            Can you do the following for me: 
                            1. Find some Italian restaurants in new york. 
                            2. Suggest any music events happening there. 
                            3. Tell me the weather forecast. 
                            4. Recommend hotels in new york. 
                            5. Suggest the best way to get around the city by public transport.
                            """,
            }
        ]
    },
):
    if chunk and "messages" in chunk:
        pretty_print_messages(chunk, last_message=True)


final_message_history = chunk["supervisor"]["messages"]
print("=== Final Answer ===")
print("Final Answer:", final_message_history[-1].content)
