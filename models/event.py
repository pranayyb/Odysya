from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel, Field


class EventItem(BaseModel):
    name: str = Field(..., description="Name or title of the event")
    date: Optional[str] = Field(None, description="Date of the event")
    venue: Optional[str] = Field(None, description="Venue where the event takes place")
    category: Optional[str] = Field(
        None, description="Type of event, e.g., concert, festival, exhibition"
    )


class Events(BaseModel):
    success: bool = Field(..., description="True if events were found; False otherwise")
    events: List[EventItem] = Field(
        default_factory=list, description="List of event details"
    )
    notes: Optional[str] = Field(
        None, description="Additional notes or reasoning about the search result"
    )
