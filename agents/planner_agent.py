import asyncio
from typing import Any
from langgraph.graph import StateGraph, START, END
from agents import HotelAgent, TransportAgent, WeatherAgent, EventAgent, RestaurantAgent
from agents.replanner_agent import ReplanAgent
from agents.itinerary_agent import ItineraryAgent
from models import (
    Itinerary,
    AgentResponse,
    PlannerState,
)


def coordinator_node(state: PlannerState) -> dict[str, Any]:
    return {}


def re_planner_node(state: PlannerState) -> dict[str, Any]:
    replan_agent = ReplanAgent()
    decision = replan_agent.analyze_planner_state(state)
    return {
        "retries": decision.retries,
        "notes": decision.notes,
        "done": decision.done,
    }


async def hotel_node(state: PlannerState) -> dict[str, Any]:
    retries = state.get("retries", [])
    if state.get("hotel_result") and "hotel" not in retries:
        return {}

    try:
        hotel_agent = HotelAgent()
        query = (
            f"Find hotels in {state['trip'].destination} from {state['trip'].start_date} "
            f"to {state['trip'].end_date} within budget {state['trip'].budget}"
        )
        response = await hotel_agent.search_and_format(query)
        return {
            "hotel_result": AgentResponse(
                agent_name="hotel",
                success=True,
                data=(
                    response.model_dump()
                    if hasattr(response, "model_dump")
                    else response
                ),
            )
        }
    except Exception as e:
        return {
            "hotel_result": AgentResponse(
                agent_name="hotel", success=False, data=None, error=str(e)
            )
        }


async def transport_node(state: PlannerState) -> dict[str, Any]:
    retries = state.get("retries", [])
    if state.get("transport_result") and "transport" not in retries:
        return {}

    try:
        transport_agent = TransportAgent()
        query = (
            f"Find transport options to reach {state['trip'].destination} "
            f"from the starting point on {state['trip'].start_date}"
        )
        response = await transport_agent.search_and_format(query)
        return {
            "transport_result": AgentResponse(
                agent_name="transport",
                success=True,
                data=(
                    response.model_dump()
                    if hasattr(response, "model_dump")
                    else response
                ),
            )
        }
    except Exception as e:
        return {
            "transport_result": AgentResponse(
                agent_name="transport", success=False, data=None, error=str(e)
            )
        }


async def restaurant_node(state: PlannerState) -> dict[str, Any]:
    retries = state.get("retries", [])
    if state.get("restaurant_result") and "restaurant" not in retries:
        return {}

    try:
        restaurant_agent = RestaurantAgent()
        query = (
            f"Find restaurants in {state['trip'].destination} suitable for {state['trip'].preferences} "
            f"during {state['trip'].start_date} to {state['trip'].end_date}"
        )
        response = await restaurant_agent.search_and_format(query)
        return {
            "restaurant_result": AgentResponse(
                agent_name="restaurant",
                success=True,
                data=(
                    response.model_dump()
                    if hasattr(response, "model_dump")
                    else response
                ),
            )
        }
    except Exception as e:
        return {
            "restaurant_result": AgentResponse(
                agent_name="restaurant", success=False, data=None, error=str(e)
            )
        }


async def weather_node(state: PlannerState) -> dict[str, Any]:
    retries = state.get("retries", [])
    if state.get("weather_result") and "weather" not in retries:
        return {}

    try:
        weather_agent = WeatherAgent()
        query = (
            f"Provide weather forecast for {state['trip'].destination} "
            f"from {state['trip'].start_date} to {state['trip'].end_date}"
        )
        response = await weather_agent.search_and_format(query)
        return {
            "weather_result": AgentResponse(
                agent_name="weather",
                success=True,
                data=(
                    response.model_dump()
                    if hasattr(response, "model_dump")
                    else response
                ),
            )
        }
    except Exception as e:
        return {
            "weather_result": AgentResponse(
                agent_name="weather", success=False, data=None, error=str(e)
            )
        }


async def event_node(state: PlannerState) -> dict[str, Any]:
    retries = state.get("retries", [])
    if state.get("event_result") and "event" not in retries:
        return {}

    try:
        event_agent = EventAgent()
        query = (
            f"Find events happening in {state['trip'].destination} "
            f"during {state['trip'].start_date} to {state['trip'].end_date}"
        )
        response = await event_agent.search_and_format(query)
        return {
            "event_result": AgentResponse(
                agent_name="event",
                success=True,
                data=(
                    response.model_dump()
                    if hasattr(response, "model_dump")
                    else response
                ),
            )
        }
    except Exception as e:
        return {
            "event_result": AgentResponse(
                agent_name="event", success=False, data=None, error=str(e)
            )
        }


def aggregator_node(state: PlannerState) -> dict[str, Any]:
    plan = Itinerary(
        trip=state["trip"],
        transport=(
            state.get("transport_result").data
            if state.get("transport_result")
            else ["No results available"]
        ),
        hotels=(
            state.get("hotel_result").data
            if state.get("hotel_result")
            else ["No results available"]
        ),
        restaurants=(
            state.get("restaurant_result").data
            if state.get("restaurant_result")
            else ["No results available"]
        ),
        weather=(
            state.get("weather_result").data
            if state.get("weather_result")
            else ["No results available"]
        ),
        events=(
            state.get("event_result").data
            if state.get("event_result")
            else ["No results available"]
        ),
    )
    return {"aggregated_plan": plan}


def itinerary_node(state: PlannerState) -> dict[str, Any]:
    try:
        itinerary_agent = ItineraryAgent()
        aggregated_plan = state.get("aggregated_plan")

        if not aggregated_plan:
            return {"final_itinerary": "Error: No aggregated plan available"}
        detailed_result = asyncio.run(
            itinerary_agent.generate_detailed_itinerary(aggregated_plan)
        )
        return {
            "final_itinerary": detailed_result,
        }
    except Exception as e:
        return {
            "final_itinerary": f"Error generating detailed itinerary: {str(e)}",
        }


graph = StateGraph(PlannerState)

graph.add_node("coordinator", coordinator_node)
graph.add_node("transport", transport_node)
graph.add_node("hotels", hotel_node)
graph.add_node("restaurants", restaurant_node)
graph.add_node("weather", weather_node)
graph.add_node("events", event_node)
graph.add_node("aggregator", aggregator_node)
graph.add_node("replanner", re_planner_node)
graph.add_node("itinerary", itinerary_node)

graph.add_edge(START, "coordinator")

graph.add_edge("coordinator", "transport")
graph.add_edge("coordinator", "hotels")
graph.add_edge("coordinator", "restaurants")
graph.add_edge("coordinator", "weather")
graph.add_edge("coordinator", "events")

graph.add_edge("transport", "coordinator")
graph.add_edge("hotels", "coordinator")
graph.add_edge("restaurants", "coordinator")
graph.add_edge("weather", "coordinator")
graph.add_edge("events", "coordinator")

graph.add_conditional_edges(
    "coordinator",
    lambda state: (
        "replanner"
        if all(
            [
                state.get("hotel_result"),
                state.get("transport_result"),
                state.get("restaurant_result"),
                state.get("weather_result"),
                state.get("event_result"),
            ]
        )
        else "wait"
    ),
    {
        "replanner": "replanner",
        "wait": "coordinator",
    },
)

graph.add_conditional_edges(
    "replanner",
    lambda state: (
        "aggregator"
        if (
            all(
                [
                    state.get("hotel_result"),
                    state.get("transport_result"),
                    state.get("restaurant_result"),
                    state.get("weather_result"),
                    state.get("event_result"),
                ]
            )
            and not state.get("retries", [])
        )
        else "coordinator"
    ),
    {
        "aggregator": "aggregator",
        "coordinator": "coordinator",
    },
)

graph.add_edge("aggregator", "itinerary")
graph.add_edge("itinerary", END)

travel_planner = graph.compile()
