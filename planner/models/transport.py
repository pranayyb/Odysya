from pydantic import BaseModel


class Transport(BaseModel):
    type: str  # e.g., "flight", "train", "car"
    provider: str
    departure: str
    arrival: str
    price: float
