from pydantic import BaseModel, Field
from typing import List, Optional


class AttractionItem(BaseModel):
    name: str = Field(..., description="Name of the tourist attraction")
    address: Optional[str] = Field(None, description="Address or locality of the attraction")
    category: Optional[str] = Field(
        None, description="Type of attraction, e.g., monument, temple, beach, park, museum"
    )
    rating: Optional[float] = Field(None, description="Average visitor rating (out of 5)")
    entry_fee: Optional[str] = Field(
        None, description="Entry fee information, e.g., '500 INR' or 'Free'"
    )
    description: Optional[str] = Field(
        None, description="Brief description of the attraction"
    )


class Attractions(BaseModel):
    success: bool = Field(
        ..., description="True if tourist attractions were found; False otherwise"
    )
    attractions: List[AttractionItem] = Field(
        default_factory=list, description="List of tourist attraction details"
    )
    notes: Optional[str] = Field(
        None, description="Additional notes or reasoning about the search result"
    )
