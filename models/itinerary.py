from pydantic import BaseModel
from typing import List
from models.hotel import Hotel
from models.restaurant import Restaurant
from models.transport import Transport
from models.event import Event
from models.weather import Weather
from models.trip_request import TripRequest


class Itinerary(BaseModel):
    trip: TripRequest
    hotels: List[Hotel] = []
    restaurants: List[Restaurant] = []
    transport: List[Transport] = []
    events: List[Event] = []
    weather: List[Weather] = []
