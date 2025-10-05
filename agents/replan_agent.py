from pydantic import BaseModel, Field
from typing import List, Dict, Any
from config import llm_model


class ReplanDecision(BaseModel):
    """Structured output schema for the re-planning decision agent."""

    retries: List[str] = Field(
        default_factory=list,
        description="Agents that should be re-run (e.g., ['hotels', 'transport'])",
    )
    adjustments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Any changes to trip parameters like budget or destination",
    )
    notes: str = Field(
        default="", description="Summary or reasoning for the replan decision"
    )
    done: bool = Field(default=False, description="Whether re-planning is complete")


from langchain_groq import ChatGroq

replan_agent = llm_model.with_structured_output(ReplanDecision)
