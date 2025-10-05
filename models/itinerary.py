from pydantic import BaseModel
from typing import List
from models.hotel import Hotel
from models.restaurant import Restaurant
from models.transport import Transport
from models.event import Events
from models.weather import Weather
from models.trip_request import TripRequest
from typing import Any


class Itinerary(BaseModel):
    trip: TripRequest
    hotels: Any = []
    restaurants: Any = []
    transport: Any = []
    events: Any = []
    weather: Any = []
