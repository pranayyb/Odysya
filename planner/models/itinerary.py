from pydantic import BaseModel
from typing import List
from models.hotel import Hotel
from models.restaurant import Restaurant
from models.transport import Transport
from models.event import Event


class Itinerary(BaseModel):
    hotels: List[Hotel] = []
    restaurants: List[Restaurant] = []
    transport: List[Transport] = []
    events: List[Event] = []
    weather_summary: str | None = None
