import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
# pyrefly: ignore [missing-import]
from langchain_core.language_models.chat_models import BaseChatModel

from agents.base import BaseAgent
from agents.base.agent_result import AgentResult
from services.microsoft.evaluation.evaluator import evaluator_service
from services.microsoft.semantic_entities.relationship import SemanticRelationship
from services.microsoft.orchestration.local_runtime import local_runtime_service

logger = logging.getLogger("data_detective.evaluation_agent")

class EvaluationAgent(BaseAgent):
    """
    Evaluation Agent responsible for measuring the platform's reasoning quality
    and ensuring completeness, determinism, and safety across the blackboard.
    """

    def __init__(self, name: str, llm: BaseChatModel, system_prompt: str = ""):
        super().__init__(
            name=name,
            llm=llm,
            system_prompt=system_prompt or "You are the Data Detective Evaluation Agent. Evaluate multi-agent execution results.",
            temperature=0.0
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoked as a LangGraph execution node. Computes evaluation metrics and registers results.
        """
        task_id = "agent_evaluation"
        start_time = self.run_telemetry_start(task_id, state)
        
        agent_start_time = time.time()
        agent_started_at = datetime.now(timezone.utc).isoformat()
        
        # Telemetry trace configuration
        root_trace_id = state.get("root_trace_id") or str(uuid.uuid4())
        evaluation_trace_id = str(uuid.uuid4())

        current_log = list(state.get("agent_execution_log") or [])
        
        # Telemetry evaluation_started
        current_log.append({
            "type": "telemetry_event",
            "event": "evaluation_started",
            "agent_name": self.name,
            "timestamp": agent_started_at
        })

        # Run evaluation service
        eval_result = evaluator_service.evaluate_state(state)
        eval_dict = eval_result.model_dump()

        agent_end_time = time.time()
        agent_completed_at = datetime.now(timezone.utc).isoformat()
        agent_duration_ms = int((agent_end_time - agent_start_time) * 1000)

        # Telemetry evaluation_completed
        current_log.append({
            "type": "telemetry_event",
            "event": "evaluation_completed",
            "agent_name": self.name,
            "timestamp": agent_completed_at
        })

        # Agent execution step log
        agent_step = {
            "type": "agent_step",
            "trace_id": evaluation_trace_id,
            "parent_trace_id": root_trace_id,
            "agent_name": self.name,
            "tool_name": None,
            "status": "completed",
            "started_at": agent_started_at,
            "completed_at": agent_completed_at,
            "duration_ms": agent_duration_ms,
            "confidence": 1.0,
            "blackboard_version": 3
        }
        current_log.append(agent_step)

        # Telemetry blackboard_updated
        current_log.append({
            "type": "telemetry_event",
            "event": "blackboard_updated",
            "agent_name": self.name,
            "timestamp": agent_completed_at
        })

        # Semantic Relationships
        relationships = list(state.get("semantic_relationships") or [])
        # EvaluationAgent creates EvaluationResult
        relationships.append(SemanticRelationship(
            relationship_id=f"rel_evaluation_creates_result",
            source_id=self.name,
            target_id="evaluation_result",
            relationship_type="creates"
        ))

        # Register capabilities with the local Foundry adapter
        local_runtime_service.register_agent(self.name, {"type": "quality_evaluator", "version": "1.0"})
        local_runtime_service.publish_trace(evaluation_trace_id, agent_step)

        # Recalculate dynamic entity count
        total_entities = 0
        if state.get("semantic_goal"):
            total_entities += 1
        if state.get("semantic_dataset"):
            total_entities += 1
            ds = state.get("semantic_dataset") or {}
            cols = ds.get("columns") or []
            total_entities += len(cols)
        
        memories = state.get("semantic_memories") or []
        semantic_issues = state.get("semantic_issues") or []
        semantic_recs = state.get("semantic_recommendations") or []
        
        total_entities += len(memories)
        total_entities += len(semantic_issues)
        total_entities += len(semantic_recs)
        
        # Phase 6 additions
        if state.get("semantic_statistics"):
            total_entities += 1
        if state.get("semantic_powerbi_readiness"):
            total_entities += 1
        total_entities += len(state.get("semantic_business_metrics") or [])
        total_entities += len(state.get("semantic_distributions") or [])
        total_entities += len(state.get("semantic_aggregation_recommendations") or [])
        
        total_entities += 1  # For evaluation_result entity itself


        prev_version = state.get("blackboard_version") or 2
        next_version = prev_version + 1

        summary_msg = f"Evaluation complete. Overall Analysis Score: {eval_result.overall_analysis_score:.2f}."
        reasoning_msg = (
            f"Evidence Completeness: {eval_result.evidence_completeness:.2f}, "
            f"Determinism: {eval_result.determinism:.2f}, "
            f"Recommendation Coverage: {eval_result.recommendation_coverage:.2f}, "
            f"Agent Agreement: {eval_result.agent_agreement:.2f}, "
            f"Trace Completeness: {eval_result.trace_completeness:.2f}."
        )

        agent_result = AgentResult(
            agent_name=self.name,
            summary=summary_msg,
            reasoning=reasoning_msg,
            confidence=1.0,
            findings=[],
            recommendations=[],
            tool_trace=[],
            execution_time_ms=agent_duration_ms
        )

        updates = {
            "evaluation_result": eval_dict,
            "agent_execution_log": current_log,
            "current_agent": "evaluation",
            "current_step": "Evaluation Complete",
            
            # Phase 5 semantic updates
            "semantic_relationships": [r.model_dump() if hasattr(r, "model_dump") else r for r in relationships],
            
            # Blackboard version info
            "blackboard_version": next_version,
            "blackboard_entity_count": total_entities,
            "blackboard_last_updated_by": self.name,
            "blackboard_last_trace_id": evaluation_trace_id
        }

        local_runtime_service.publish_memory(next_version, updates)
        self.run_telemetry_end(task_id, start_time, updates, tokens=80)
        return updates
