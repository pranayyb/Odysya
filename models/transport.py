from pydantic import BaseModel, Field
from typing import List, Optional


class TransportItem(BaseModel):
    mode: str = Field(..., description="Mode of transport, e.g., bus, train, flight")
    name: str = Field(..., description="Name or identifier of the transport option")
    departure: Optional[str] = Field(None, description="Departure time or location")
    arrival: Optional[str] = Field(None, description="Arrival time or location")
    duration: Optional[str] = Field(None, description="Duration of the journey")
    price: Optional[str] = Field(
        None, description="Price or fare for the transport option"
    )


class Transport(BaseModel):
    success: bool = Field(
        ..., description="True if transport options were found; False otherwise"
    )
    transport: List[TransportItem] = Field(
        default_factory=list, description="List of transport options"
    )
    notes: Optional[str] = Field(
        None, description="Additional notes about the search result"
    )
