from pydantic import BaseModel, Field
from typing import List, Optional


class WeatherItem(BaseModel):
    date: str = Field(..., description="Date of the weather forecast")
    temperature: Optional[str] = Field(None, description="Temperature, e.g., '25°C'")
    condition: Optional[str] = Field(
        None, description="Weather condition, e.g., sunny, rainy"
    )
    humidity: Optional[str] = Field(None, description="Humidity percentage")
    wind: Optional[str] = Field(
        None, description="Wind information, e.g., '10 km/h NE'"
    )


class Weather(BaseModel):
    success: bool = Field(
        ..., description="True if weather information was found; False otherwise"
    )
    weather: List[WeatherItem] = Field(
        default_factory=list, description="List of weather details"
    )
    notes: Optional[str] = Field(
        None, description="Additional notes about the search result"
    )
