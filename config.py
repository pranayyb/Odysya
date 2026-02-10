import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

llm_model = ChatGroq(
    model=MODEL_NAME,
    api_key=os.getenv("GROQ_API_KEY"),
)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
YELP_API_KEY = os.getenv("YELP_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
EVENTS_API_KEY = os.getenv("EVENTS_API_KEY", "")
TRANSPORT_API_KEY = os.getenv("TRANSPORT_API_KEY", "")

BOOKING_API_BASE = "https://booking-com.p.rapidapi.com/v1"
YELP_API_BASE = "https://api.yelp.com/v3"
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
EVENTS_API_BASE = "https://events-api.example.com/v1"
TRANSPORT_API_BASE = "https://transport-api.example.com/v1"

TRANSPORT_MOCK_BOOL = os.getenv("TRANSPORT_MOCK", "True")
WEATHER_MOCK_BOOL = os.getenv("WEATHER_MOCK", "True")
RESTAURANT_MOCK_BOOL = os.getenv("RESTAURANT_MOCK", "True")
EVENT_MOCK_BOOL = os.getenv("EVENT_MOCK", "True")
HOTEL_MOCK_BOOL = os.getenv("HOTEL_MOCK", "True")

MAX_AGENT_RETRIES = int(os.getenv("MAX_AGENT_RETRIES", "3"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = "logs"

USER_PROFILES_DIR = "data/user_profiles"
