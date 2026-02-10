import asyncio
from typing import Any
from langgraph.graph import StateGraph, START, END
from agents import HotelAgent, TransportAgent, WeatherAgent, EventAgent, RestaurantAgent
from agents.replanner_agent import ReplanAgent
from agents.itinerary_agent import ItineraryAgent
from config import MAX_AGENT_RETRIES
from utils.logger import get_logger
from models import (
    Itinerary,
    AgentResponse,
    PlannerState,
)

logger = get_logger("PlannerAgent")


def coordinator_node(state: PlannerState) -> dict[str, Any]:
    logger.info("coordinator_node entered")
    retry_count = state.get("retry_count", 0)
    logger.info(
        f"coordinator_node | retry_count={retry_count} | retries={state.get('retries', [])}"
    )
    return {}


def re_planner_node(state: PlannerState) -> dict[str, Any]:
    retry_count = state.get("retry_count", 0)
    logger.info(
        f"re_planner_node entered | retry_count={retry_count}/{MAX_AGENT_RETRIES}"
    )

    if retry_count >= MAX_AGENT_RETRIES:
        logger.warning(
            f"Max retries ({MAX_AGENT_RETRIES}) reached — forcing completion"
        )
        return {
            "retries": [],
            "notes": f"Max retries ({MAX_AGENT_RETRIES}) reached. Proceeding with best available data.",
            "done": True,
            "retry_count": retry_count,
        }

    replan_agent = ReplanAgent()
    decision = replan_agent.analyze_planner_state(state)
    logger.info(
        f"re_planner_node decision | done={decision.done} | retries={decision.retries} | notes={decision.notes[:100]}..."
    )

    new_retry_count = retry_count + (1 if decision.retries else 0)

    return {
        "retries": decision.retries,
        "notes": decision.notes,
        "done": decision.done,
        "retry_count": new_retry_count,
    }


async def hotel_node(state: PlannerState) -> dict[str, Any]:
    retries = state.get("retries", [])
    if state.get("hotel_result") and "hotel" not in retries:
        logger.debug("hotel_node skipped — result exists and no retry requested")
        return {}

    logger.info("hotel_node started")
    try:
        hotel_agent = HotelAgent()
        query = (
            f"Find hotels in {state['trip'].destination} from {state['trip'].start_date} "
            f"to {state['trip'].end_date} within budget {state['trip'].budget}"
        )
        response = await hotel_agent.search_and_format(query)
        logger.info("hotel_node completed successfully")
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
        logger.error(f"hotel_node failed | error={e}")
        return {
            "hotel_result": AgentResponse(
                agent_name="hotel", success=False, data=None, error=str(e)
            )
        }


async def transport_node(state: PlannerState) -> dict[str, Any]:
    retries = state.get("retries", [])
    if state.get("transport_result") and "transport" not in retries:
        logger.debug("transport_node skipped — result exists and no retry requested")
        return {}

    logger.info("transport_node started")
    try:
        transport_agent = TransportAgent()
        query = (
            f"Find transport options to reach {state['trip'].destination} "
            f"from the starting point on {state['trip'].start_date}"
        )
        response = await transport_agent.search_and_format(query)
        logger.info("transport_node completed successfully")
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
        logger.error(f"transport_node failed | error={e}")
        return {
            "transport_result": AgentResponse(
                agent_name="transport", success=False, data=None, error=str(e)
            )
        }


async def restaurant_node(state: PlannerState) -> dict[str, Any]:
    retries = state.get("retries", [])
    if state.get("restaurant_result") and "restaurant" not in retries:
        logger.debug("restaurant_node skipped — result exists and no retry requested")
        return {}

    logger.info("restaurant_node started")
    try:
        restaurant_agent = RestaurantAgent()
        query = (
            f"Find restaurants in {state['trip'].destination} suitable for {state['trip'].preferences} "
            f"during {state['trip'].start_date} to {state['trip'].end_date}"
        )
        response = await restaurant_agent.search_and_format(query)
        logger.info("restaurant_node completed successfully")
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
        logger.error(f"restaurant_node failed | error={e}")
        return {
            "restaurant_result": AgentResponse(
                agent_name="restaurant", success=False, data=None, error=str(e)
            )
        }


async def weather_node(state: PlannerState) -> dict[str, Any]:
    retries = state.get("retries", [])
    if state.get("weather_result") and "weather" not in retries:
        logger.debug("weather_node skipped — result exists and no retry requested")
        return {}

    logger.info("weather_node started")
    try:
        weather_agent = WeatherAgent()
        query = (
            f"Provide weather forecast for {state['trip'].destination} "
            f"from {state['trip'].start_date} to {state['trip'].end_date}"
        )
        response = await weather_agent.search_and_format(query)
        logger.info("weather_node completed successfully")
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
        logger.error(f"weather_node failed | error={e}")
        return {
            "weather_result": AgentResponse(
                agent_name="weather", success=False, data=None, error=str(e)
            )
        }


async def event_node(state: PlannerState) -> dict[str, Any]:
    retries = state.get("retries", [])
    if state.get("event_result") and "event" not in retries:
        logger.debug("event_node skipped — result exists and no retry requested")
        return {}

    logger.info("event_node started")
    try:
        event_agent = EventAgent()
        query = (
            f"Find events happening in {state['trip'].destination} "
            f"during {state['trip'].start_date} to {state['trip'].end_date}"
        )
        response = await event_agent.search_and_format(query)
        logger.info("event_node completed successfully")
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
        logger.error(f"event_node failed | error={e}")
        return {
            "event_result": AgentResponse(
                agent_name="event", success=False, data=None, error=str(e)
            )
        }


def aggregator_node(state: PlannerState) -> dict[str, Any]:
    logger.info("aggregator_node entered")

    result_keys = [
        "hotel_result",
        "transport_result",
        "restaurant_result",
        "weather_result",
        "event_result",
    ]
    for key in result_keys:
        result = state.get(key)
        if result and not result.success:
            logger.warning(
                f"aggregator_node | {key} has failed status — using fallback data"
            )

    plan = Itinerary(
        trip=state["trip"],
        transport=(
            state.get("transport_result").data
            if state.get("transport_result") and state.get("transport_result").data
            else ["No results available"]
        ),
        hotels=(
            state.get("hotel_result").data
            if state.get("hotel_result") and state.get("hotel_result").data
            else ["No results available"]
        ),
        restaurants=(
            state.get("restaurant_result").data
            if state.get("restaurant_result") and state.get("restaurant_result").data
            else ["No results available"]
        ),
        weather=(
            state.get("weather_result").data
            if state.get("weather_result") and state.get("weather_result").data
            else ["No results available"]
        ),
        events=(
            state.get("event_result").data
            if state.get("event_result") and state.get("event_result").data
            else ["No results available"]
        ),
    )
    logger.info("aggregator_node completed — plan assembled")
    return {"aggregated_plan": plan}


async def itinerary_node(state: PlannerState) -> dict[str, Any]:
    logger.info("itinerary_node entered")
    try:
        itinerary_agent = ItineraryAgent()
        aggregated_plan = state.get("aggregated_plan")

        if not aggregated_plan:
            logger.error("itinerary_node | No aggregated plan available")
            return {"final_itinerary": "Error: No aggregated plan available"}

        detailed_result = await itinerary_agent.generate_detailed_itinerary(
            aggregated_plan
        )
        logger.info("itinerary_node completed successfully")
        return {
            "final_itinerary": detailed_result,
        }
    except Exception as e:
        logger.error(f"itinerary_node failed | error={e}")
        return {
            "final_itinerary": f"Error generating detailed itinerary: {str(e)}",
        }


def route_after_replanner(state: PlannerState) -> str:
    retries = state.get("retries", [])
    done = state.get("done", False)
    retry_count = state.get("retry_count", 0)

    if done or retry_count >= MAX_AGENT_RETRIES:
        logger.info(
            f"route_after_replanner -> aggregator | done={done} | retry_count={retry_count}"
        )
        return "aggregator"

    if retries:
        logger.info(f"route_after_replanner -> coordinator | retries={retries}")
        return "coordinator"

    logger.info("route_after_replanner -> aggregator (no retries needed)")
    return "aggregator"


logger.info("Building travel planner graph...")

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

graph.add_edge("transport", "replanner")
graph.add_edge("hotels", "replanner")
graph.add_edge("restaurants", "replanner")
graph.add_edge("weather", "replanner")
graph.add_edge("events", "replanner")

graph.add_conditional_edges(
    "replanner",
    route_after_replanner,
    {
        "aggregator": "aggregator",
        "coordinator": "coordinator",
    },
)

graph.add_edge("aggregator", "itinerary")
graph.add_edge("itinerary", END)

travel_planner = graph.compile()
logger.info("Travel planner graph compiled successfully")
