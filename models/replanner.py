from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ReplanDecision(BaseModel):
    retries: List[str] = Field(
        default_factory=list,
        description="Agents that should be re-run (e.g., ['hotel', 'transport', 'restaurant', 'weather', 'event'])",
    )
    adjustments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Any changes to trip parameters like budget or destination",
    )
    issues_identified: List[str] = Field(
        default_factory=list,
        description="List of specific issues found with current results",
    )
    notes: str = Field(
        default="", description="Summary or additional notes for the replan decision"
    )
    done: bool = Field(default=False, description="Whether re-planning is complete")
