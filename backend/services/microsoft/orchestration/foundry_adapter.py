from abc import ABC, abstractmethod
from typing import Any, Dict, List

class FoundryAdapterInterface(ABC):
    """
    Interface defining the Foundry-compatible orchestration adapter contract.
    Ensures provider-agnostic execution tracing, agent registrations, and blackboard snapshots.
    """

    @abstractmethod
    def register_agent(self, agent_name: str, config: Dict[str, Any]) -> None:
        """
        Registers agent capabilities, name, and configuration details.
        """
        pass

    @abstractmethod
    def execute_workflow(self, workflow_name: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Starts a managed multi-agent execution pipeline.
        """
        pass

    @abstractmethod
    def publish_trace(self, trace_id: str, trace_data: Dict[str, Any]) -> None:
        """
        Publishes telemetry traces for active node and tool executions.
        """
        pass

    @abstractmethod
    def publish_memory(self, blackboard_version: int, memory_data: Dict[str, Any]) -> None:
        """
        Saves a point-in-time snapshot of the shared blackboard memory.
        """
        pass

    @abstractmethod
    def register_statistics_agent(self, agent_name: str, config: Dict[str, Any]) -> None:
        """
        Registers the Business Intelligence / Readiness agent capabilities.
        """
        pass

    @abstractmethod
    def publish_statistics_entities(self, blackboard_version: int, entities: List[Dict[str, Any]]) -> None:
        """
        Publishes distribution and metric entities.
        """
        pass

    @abstractmethod
    def publish_powerbi_readiness(self, blackboard_version: int, readiness_data: Dict[str, Any]) -> None:
        """
        Publishes Power BI readiness metrics.
        """
        pass

