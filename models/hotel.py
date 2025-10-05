from pydantic import BaseModel, Field
from typing import List, Optional


class HotelItem(BaseModel):
    name: str = Field(..., description="Name of the hotel")
    address: Optional[str] = Field(None, description="Address of the hotel")
    rating: Optional[float] = Field(
        None, description="Rating of the hotel (e.g., 4.5/5)"
    )
    amenities: Optional[List[str]] = Field(
        None, description="List of amenities available"
    )
    price_range: Optional[str] = Field(None, description="Price range of the hotel")


class Hotels(BaseModel):
    success: bool = Field(..., description="True if hotels were found; False otherwise")
    hotels: List[HotelItem] = Field(
        default_factory=list, description="List of hotel details"
    )
    notes: Optional[str] = Field(
        None, description="Additional notes about the search result"
    )
