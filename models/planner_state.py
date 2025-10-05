from typing import Dict, TypedDict

from models.agent_response import AgentResponse
from models.trip_request import TripRequest


class PlannerState(TypedDict):
    trip: TripRequest
    results: Dict[str, AgentResponse]
    retries: list[str]
    done: bool
