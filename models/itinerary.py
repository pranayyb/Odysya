from pydantic import BaseModel
from typing import List
from models.trip_request import TripRequest
from typing import Any


class Itinerary(BaseModel):
    trip: TripRequest
    hotels: Any = []
    restaurants: Any = []
    transport: Any = []
    events: Any = []
    attractions: Any = []
    weather: Any = []
