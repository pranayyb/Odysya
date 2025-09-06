from pydantic import BaseModel
from typing import Any


class AgentResponse(BaseModel):
    agent_name: str
    success: bool
    data: Any
    error: str | None = None
