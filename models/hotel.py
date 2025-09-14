from pydantic import BaseModel


class Hotel(BaseModel):
    name: str
    address: str
    price_per_night: float
    rating: float
    link: str
