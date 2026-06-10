from pydantic import BaseModel, Field
from typing import List, Any

class AgentResult(BaseModel):
    """
    Standardized result contract returned by every agent node in the multi-agent system.
    Enforces consistency and predictability for UI rendering and agent interaction.
    """
    agent_name: str
    summary: str
    reasoning: str
    confidence: float
    findings: List[Any] = Field(default_factory=list)
    recommendations: List[Any] = Field(default_factory=list)
    tool_trace: List[Any] = Field(default_factory=list)
    execution_time_ms: int
