from pydantic import BaseModel


class Event(BaseModel):
    name: str
    category: str
    location: str
    date: str
    price: float | None = None
