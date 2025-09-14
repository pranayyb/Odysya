import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"

llm_model = ChatGroq(
    model=MODEL_NAME,
    api_key=os.getenv("GROQ_API_KEY"),
)

TRANSPORT_MOCK_BOOL = True
WEATHER_MOCK_BOOL = True
RESTAURANT_MOCK_BOOL = True
EVENT_MOCK_BOOL = True
HOTEL_MOCK_BOOL = True
