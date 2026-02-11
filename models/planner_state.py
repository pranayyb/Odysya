from typing import Dict, TypedDict, Any

from models.agent_response import AgentResponse
from models.trip_request import TripRequest
from models.itinerary import Itinerary


class PlannerState(TypedDict):
    trip: TripRequest
    hotel_result: AgentResponse | None
    transport_result: AgentResponse | None
    restaurant_result: AgentResponse | None
    weather_result: AgentResponse | None
    event_result: AgentResponse | None
    attraction_result: AgentResponse | None
    retries: list[str]
    retry_count: int
    notes: str
    done: bool
    aggregated_plan: Itinerary | None
    final_itinerary: Dict[str, Any] | None

    @staticmethod
    def create(trip: TripRequest) -> "PlannerState":
        return PlannerState(
            trip=trip,
            retries=[],
            retry_count=0,
            done=False,
            notes="",
            hotel_result=None,
            transport_result=None,
            restaurant_result=None,
            weather_result=None,
            event_result=None,
            attraction_result=None,
            aggregated_plan=None,
            final_itinerary=None,
        )
