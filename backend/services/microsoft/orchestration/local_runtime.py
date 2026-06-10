import logging
from typing import Any, Dict, List
from services.microsoft.orchestration.foundry_adapter import FoundryAdapterInterface

logger = logging.getLogger("data_detective.orchestration")

class LocalRuntime(FoundryAdapterInterface):
    """
    Local developer runtime implementing the FoundryAdapterInterface.
    Performs fully local tracking of registered agents, traces, and blackboard version history.
    """

    def __init__(self):
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.published_traces: Dict[str, Dict[str, Any]] = {}
        self.memory_snapshots: Dict[int, Dict[str, Any]] = {}

    def register_agent(self, agent_name: str, config: Dict[str, Any]) -> None:
        self.registered_agents[agent_name] = config
        logger.info(f"[Foundry Registry] Agent '{agent_name}' registered locally: {config}")

    def execute_workflow(self, workflow_name: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[Foundry Orchestrator] Triggered local workflow run '{workflow_name}'")
        return initial_state

    def publish_trace(self, trace_id: str, trace_data: Dict[str, Any]) -> None:
        self.published_traces[trace_id] = trace_data
        logger.info(f"[Foundry Tracing] Trace published [ID: {trace_id}] - Agent: {trace_data.get('agent')}, Tool: {trace_data.get('tool')}, Duration: {trace_data.get('duration_ms')} ms")

    def publish_memory(self, blackboard_version: int, memory_data: Dict[str, Any]) -> None:
        self.memory_snapshots[blackboard_version] = memory_data
        logger.info(f"[Foundry Semantic Memory] Snapshot published [Version: {blackboard_version}] - last_updated_by: {memory_data.get('last_updated_by')}")

    def register_statistics_agent(self, agent_name: str, config: Dict[str, Any]) -> None:
        self.registered_agents[agent_name] = config
        logger.info(f"[Foundry Registry] BI Readiness Agent '{agent_name}' registered: {config}")

    def publish_statistics_entities(self, blackboard_version: int, entities: List[Dict[str, Any]]) -> None:
        logger.info(f"[Foundry Semantic Memory] Published {len(entities)} statistics entities for Blackboard v{blackboard_version}")

    def publish_powerbi_readiness(self, blackboard_version: int, readiness_data: Dict[str, Any]) -> None:
        score = readiness_data.get("readiness_score")
        status = readiness_data.get("overall_rating_text")
        logger.info(f"[Foundry Tracing] Published Power BI readiness score: {score}% [Status: {status}] for Blackboard v{blackboard_version}")


# Instantiate global service singleton
local_runtime_service = LocalRuntime()
