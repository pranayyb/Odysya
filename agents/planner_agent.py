from typing import Any
from langgraph.graph import StateGraph, START, END

from agents import (
    hotel_agent,
    transport_agent,
    restaurant_agent,
    weather_agent,
    event_agent,
)

from models import (
    TripRequest,
    Itinerary,
    AgentResponse,
    PlannerState,
    Weather,
    Event,
    Hotel,
    Transport,
    Restaurant,
)


def root_node(state: PlannerState) -> dict[str, Any]:
    retries = []
    for agent_key in [
        "hotel_result",
        "transport_result",
        "restaurant_result",
        "weather_result",
        "event_result",
    ]:
        agent_data = state.get(agent_key)
        if not agent_data or not agent_data.success:
            retries.append(agent_key.split("_")[0])

    if retries:
        return {"retries": retries, "done": False}
    else:
        return {"done": True}


def hotel_node(state: PlannerState) -> dict[str, Any]:
    query = (
        f"Find hotels in {state['trip'].destination} from {state['trip'].start_date} "
        f"to {state['trip'].end_date} within budget {state['trip'].budget}"
    )
    response = hotel_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )
    return {
        "hotel_result": AgentResponse(
            agent_name="hotel", success=True, data=response["messages"][0].content
        )
    }


def transport_node(state: PlannerState) -> dict[str, Any]:
    query = (
        f"Find transport options to reach {state['trip'].destination} "
        f"from the starting point on {state['trip'].start_date}"
    )
    response = transport_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )
    transport_data = response["messages"][0].content
    return {
        "transport_result": AgentResponse(
            agent_name="transport", success=True, data=transport_data
        )
    }


def restaurant_node(state: PlannerState) -> dict[str, Any]:
    query = (
        f"Find restaurants in {state['trip'].destination} suitable for {state['trip'].preferences} "
        f"during {state['trip'].start_date} to {state['trip'].end_date}"
    )
    response = restaurant_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )
    restaurant_data = response["messages"][0].content
    return {
        "restaurant_result": AgentResponse(
            agent_name="restaurant", success=True, data=restaurant_data
        )
    }


def weather_node(state: PlannerState) -> dict[str, Any]:
    query = (
        f"Provide weather forecast for {state['trip'].destination} "
        f"from {state['trip'].start_date} to {state['trip'].end_date}"
    )
    response = weather_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )
    weather_data = response["messages"][0].content
    return {
        "weather_result": AgentResponse(
            agent_name="weather", success=True, data=weather_data
        )
    }


def event_node(state: PlannerState) -> dict[str, Any]:
    query = (
        f"Find events happening in {state['trip'].destination} "
        f"during {state['trip'].start_date} to {state['trip'].end_date}"
    )
    response = event_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )
    event_data = response["messages"][0].content
    return {
        "event_result": AgentResponse(
            agent_name="events", success=True, data=event_data
        )
    }


def aggregator_node(state: PlannerState) -> dict[str, Any]:
    plan = Itinerary(
        trip=state["trip"],
        transport=(
            state.get("transport_result").data if state.get("transport_result") else []
        ),
        hotels=state.get("hotel_result").data if state.get("hotel_result") else [],
        restaurants=(
            state.get("restaurant_result").data
            if state.get("restaurant_result")
            else []
        ),
        weather=state.get("weather_result").data if state.get("weather_result") else [],
        events=state.get("event_result").data if state.get("event_result") else [],
    )
    print("\nFinal Trip Plan:\n", plan.model_dump_json(indent=2))
    return {"plan": plan}


graph = StateGraph(PlannerState)

graph.add_node("root", root_node)
graph.add_node("transport", transport_node)
graph.add_node("hotels", hotel_node)
graph.add_node("restaurants", restaurant_node)
graph.add_node("weather", weather_node)
graph.add_node("events", event_node)
graph.add_node("aggregator", aggregator_node)

graph.add_edge(START, "root")

for agent in ["transport", "hotels", "restaurants", "weather", "events"]:
    graph.add_edge("root", agent)
    graph.add_edge(agent, "aggregator")

# graph.add_edge("root", "aggregator")

travel_planner = graph.compile()


if __name__ == "__main__":
    trip_request = TripRequest(
        destination="Goa",
        start_date="2025-06-01",
        end_date="2025-06-05",
        preferences=["beach", "food"],
        budget=2000.0,
    )
    initial_state = {"trip": trip_request, "retries": [], "done": False}
    travel_planner.invoke(initial_state, {"recursion_limit": 50})


# Root node to check which agents need retry
# def root_node(state: PlannerState) -> dict[str, Any]:
#     retries = []

#     # If no results yet, trigger all agents
#     if not any(
#         key in state
#         for key in [
#             "hotel_result",
#             "transport_result",
#             "restaurant_result",
#             "weather_result",
#             "event_result",
#         ]
#     ):
#         return {
#             "retries": ["transport", "hotel", "restaurant", "weather", "event"],
#             "done": False,
#         }

#     # for agent_key in [
#     #     "hotel_result",
#     #     "transport_result",
#     #     "restaurant_result",
#     #     "weather_result",
#     #     "event_result",
#     # ]:
#     #     agent_data = state.get(agent_key)
#     #     if not agent_data or not agent_data.success:
#     #         retries.append(agent_key.split("_")[0])


#     # if retries:
#     #     return {"retries": list(set(retries)), "done": False}
#     # else:
#     #     return {"done": True}
