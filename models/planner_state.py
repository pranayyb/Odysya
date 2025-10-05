from typing import Dict, TypedDict

from models.agent_response import AgentResponse
from models.trip_request import TripRequest
from models.itinerary import Itinerary


class PlannerState(TypedDict):
    trip: TripRequest
    # results: Dict[str, AgentResponse]
    hotel_result: AgentResponse | None
    transport_result: AgentResponse | None
    restaurant_result: AgentResponse | None
    weather_result: AgentResponse | None
    event_result: AgentResponse | None
    retries: list[str]
    notes: str
    done: bool
    plan: Itinerary | None
