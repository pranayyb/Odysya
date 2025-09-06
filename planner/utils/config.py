import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    HOTEL_API_KEY = os.getenv("HOTEL_API_KEY")
    RESTAURANT_API_KEY = os.getenv("RESTAURANT_API_KEY")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    TRANSPORT_API_KEY = os.getenv("TRANSPORT_API_KEY")
    EVENT_API_KEY = os.getenv("EVENT_API_KEY")
