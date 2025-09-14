from pydantic import BaseModel


class Weather(BaseModel):
    date: str
    summary: str
    temperature_high: float
    temperature_low: float
