from pydantic import BaseModel
from typing import List

class TripRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    preferences: List[str] = []
    budget: float | None = None
