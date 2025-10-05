from pydantic import BaseModel, Field
from typing import List, Optional


class RestaurantItem(BaseModel):
    name: str = Field(..., description="Name of the restaurant")
    address: Optional[str] = Field(None, description="Address of the restaurant")
    cuisine: Optional[str] = Field(None, description="Type of cuisine served")
    rating: Optional[float] = Field(None, description="Rating of the restaurant")
    price_range: Optional[str] = Field(
        None, description="Price range of the restaurant"
    )


class Restaurants(BaseModel):
    success: bool = Field(
        ..., description="True if restaurants were found; False otherwise"
    )
    restaurants: List[RestaurantItem] = Field(
        default_factory=list, description="List of restaurant details"
    )
    notes: Optional[str] = Field(
        None, description="Additional notes about the search result"
    )
