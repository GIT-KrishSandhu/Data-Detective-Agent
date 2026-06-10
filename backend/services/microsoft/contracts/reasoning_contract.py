from abc import ABC, abstractmethod
from typing import Any, Dict, List
from agents.base.agent_result import AgentResult

class ReasoningContract(ABC):
    """
    Standard interface contract that all worker agents in the platform must support.
    Ensures they execute transparently, record tool execution traces, and output consistent AgentResults.
    """

    @abstractmethod
    async def analyze_with_evidence(self, data: Any, context: Dict[str, Any]) -> AgentResult:
        """
        Executes analysis, records deterministic tool events, and builds an AgentResult
        containing evidence-backed findings and recommendations.
        """
        pass
