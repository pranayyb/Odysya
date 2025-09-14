from pydantic import BaseModel


class Restaurant(BaseModel):
    name: str
    cuisine: str
    rating: float
    address: str
    price_level: str
