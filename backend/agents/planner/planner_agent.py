import logging
from typing import Any, Dict, List
from langchain_core.language_models.chat_models import BaseChatModel

from agents.base import BaseAgent

logger = logging.getLogger("data_detective.planner")

# Standard static workflow steps templates per goal type
GOAL_WORKFLOWS = {
    "Data Quality Audit": [
        "Schema Analysis",
        "Missing Values Scan",
        "Type Validation",
        "Anomaly Detection",
        "Quality Reporting"
    ],
    "Exploratory Data Analysis": [
        "Descriptive Profiling",
        "Distribution Scan",
        "Outliers Profiling",
        "Correlation Analysis",
        "Insights Formulation"
    ],
    "Executive Summary": [
        "Structural Metrics Profiling",
        "Key Outliers Summary",
        "Critical Findings Synthesis",
        "Recommendation Outlines",
        "Summary Formatting"
    ],
    "Power BI Preparation": [
        "Schema Analysis",
        "Data Quality Analysis",
        "Statistics Analysis",
        "Visualization Planning",
        "Dashboard Recommendations"
    ]
}

class PlannerAgent(BaseAgent):
    """
    Reasoning layer agent responsible for interpreting goals,
    analyzing dataset metadata, and generating step-by-step workflow schedules.
    """

    def __init__(self, name: str, llm: BaseChatModel, system_prompt: str = ""):
        super().__init__(
            name=name,
            llm=llm,
            system_prompt=system_prompt or "You are the Data Detective Planner Agent. Create a step-by-step workflow plan.",
            temperature=0.0
        )

    def plan_workflow(
        self, 
        goal: str, 
        metadata: Dict[str, Any], 
        profile_summary: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Generates analysis steps, explains the logic of selection based on profile metrics,
        and computes confidence scores.
        """
        # Determine fallback default workflow if goal matches partially or is invalid
        goal_lower = goal.lower()
        matched_goal = "Data Quality Audit"
        
        if "quality" in goal_lower:
            matched_goal = "Data Quality Audit"
        elif "eda" in goal_lower or "exploratory" in goal_lower:
            matched_goal = "Exploratory Data Analysis"
        elif "summary" in goal_lower or "executive" in goal_lower:
            matched_goal = "Executive Summary"
        elif "power" in goal_lower or "bi" in goal_lower:
            matched_goal = "Power BI Preparation"
        else:
            for key in GOAL_WORKFLOWS.keys():
                if key.lower() in goal_lower:
                    matched_goal = key
                    break
        
        steps = GOAL_WORKFLOWS[matched_goal]

        # 1. Deterministic reasoning construction
        num_cols = profile_summary.get("numeric_columns", 0)
        cat_cols = profile_summary.get("categorical_columns", 0)
        dt_cols = profile_summary.get("datetime_columns", 0)
        missing_cols = profile_summary.get("columns_with_missing_values", 0)

        reasoning_points = []
        reasoning_points.append(
            f"Selected workflow schedule '{matched_goal}' based on analytical objective."
        )
        
        if missing_cols > 0:
            reasoning_points.append(
                f"Prioritized missing values check because {missing_cols} columns contain null/missing cells."
            )
        else:
            reasoning_points.append(
                "Skipped dense null scanning as all column values are fully complete (0 missing)."
            )

        if num_cols > 0:
            reasoning_points.append(
                f"Prioritized numerical analysis and correlation mapping due to presence of {num_cols} numeric columns."
            )
        if dt_cols > 0:
            reasoning_points.append(
                f"Prioritized temporal index profiling since the dataset has {dt_cols} datetime columns."
            )

        reasoning_str = " • ".join(reasoning_points)

        # 2. Compute confidence score
        # Confidence decreases slightly if there is high schema complexity or high null rates,
        # indicating more verification checks will be required downstream.
        base_confidence = 0.95
        if missing_cols > 0:
            base_confidence -= 0.05
        if profile_summary.get("columns_with_missing_values", 0) > 3:
            base_confidence -= 0.05
        
        confidence = max(0.60, min(1.0, base_confidence))

        # Emit telemetry placeholders
        logger.info(f"[Telemetry] event=planner_started goal={goal}")
        logger.info(f"[Telemetry] event=workflow_generated steps={steps}")
        logger.info(f"[Telemetry] event=planner_completed confidence={confidence}")

        return {
            "goal": matched_goal,
            "reasoning": reasoning_str,
            "workflow_steps": steps,
            "confidence": round(confidence, 2)
        }

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoked as a LangGraph execution node. Modifies AgentState.
        """
        import time
        import uuid
        from datetime import datetime, timezone
        from agents.base.agent_result import AgentResult
        
        # Import semantic entities and relationships
        from services.microsoft.semantic_entities.analysis_goal import AnalysisGoalEntity
        from services.microsoft.semantic_entities.dataset_entity import DatasetEntity, ColumnEntity
        from services.microsoft.semantic_entities.agent_memory import AgentMemoryEntity
        from services.microsoft.semantic_entities.relationship import SemanticRelationship
        from services.microsoft.orchestration.local_runtime import local_runtime_service

        start_time_sec = time.time()
        started_at_str = datetime.now(timezone.utc).isoformat()

        # Telemetry trace configuration
        root_trace_id = state.get("root_trace_id") or str(uuid.uuid4())
        planner_trace_id = str(uuid.uuid4())

        task_id = "agent_planning"
        start_time = self.run_telemetry_start(task_id, state)

        goal = state.get("goal") or "Data Quality Audit"
        metadata = state.get("dataset_metadata") or {}
        dataset_id = state.get("dataset_id") or str(uuid.uuid4())
        profile_summary = state.get("profile_summary") or {
            "numeric_columns": 0,
            "categorical_columns": 0,
            "datetime_columns": 0,
            "boolean_columns": 0,
            "columns_with_missing_values": 0
        }

        # Calculate workflow
        plan_res = self.plan_workflow(goal, metadata, profile_summary)

        end_time_sec = time.time()
        completed_at_str = datetime.now(timezone.utc).isoformat()
        execution_time_ms = int((end_time_sec - start_time_sec) * 1000)

        # 1. Create Semantic Goal Entity
        goal_entity = AnalysisGoalEntity(
            entity_id=f"goal_{dataset_id}",
            entity_type="AnalysisGoal",
            created_by_agent=self.name,
            goal_text=goal,
            target_metric=None,
            priority_level="Medium",
            confidence=plan_res["confidence"]
        )

        # 2. Create Dataset and Column Entities
        schema_info = state.get("schema_info") or []
        column_entities = []
        relationships = list(state.get("semantic_relationships") or [])
        
        for col in schema_info:
            col_name = col.get("name")
            col_entity = ColumnEntity(
                name=col_name,
                inferred_type=col.get("inferred_type", "object"),
                null_count=col.get("null_count", 0),
                null_percentage=col.get("null_percentage", 0.0),
                unique_values=col.get("unique_values", 0),
                sample_values=col.get("sample_values") or []
            )
            column_entities.append(col_entity)
            
            # Dataset contains Column relationship
            relationships.append(SemanticRelationship(
                relationship_id=f"rel_dataset_contains_col_{col_name}",
                source_id=f"dataset_{dataset_id}",
                target_id=f"col_{col_name}",
                relationship_type="contains"
            ))

        dataset_entity = DatasetEntity(
            entity_id=f"dataset_{dataset_id}",
            entity_type="Dataset",
            created_by_agent=self.name,
            filename=metadata.get("filename", "unknown"),
            file_path=state.get("dataset_path", "unknown"),
            file_size_bytes=metadata.get("file_size_bytes", 0),
            row_count=metadata.get("row_count", 0),
            column_count=metadata.get("column_count", 0),
            detected_type=metadata.get("detected_type", "csv"),
            columns=column_entities
        )

        # 3. Create Agent Memory Entity
        memory_entity = AgentMemoryEntity(
            entity_id=f"memory_planner_{dataset_id}",
            entity_type="AgentMemory",
            created_by_agent=self.name,
            agent_name=self.name,
            cognitive_state="Planner workflow schedule generated successfully.",
            internal_variables={"goal": plan_res["goal"], "workflow_steps": plan_res["workflow_steps"]},
            confidence=plan_res["confidence"],
            dependencies=[goal_entity.entity_id, dataset_entity.entity_id]
        )

        # 4. Agent Creates Entity Relationships
        relationships.append(SemanticRelationship(
            relationship_id=f"rel_planner_creates_goal_{dataset_id}",
            source_id=self.name,
            target_id=goal_entity.entity_id,
            relationship_type="creates"
        ))
        relationships.append(SemanticRelationship(
            relationship_id=f"rel_planner_creates_dataset_{dataset_id}",
            source_id=self.name,
            target_id=dataset_entity.entity_id,
            relationship_type="creates"
        ))
        relationships.append(SemanticRelationship(
            relationship_id=f"rel_planner_creates_memory_{dataset_id}",
            source_id=self.name,
            target_id=memory_entity.entity_id,
            relationship_type="creates"
        ))

        # 5. Build AgentResult conforming to the shared contract
        agent_result = AgentResult(
            agent_name=self.name,
            summary=f"Selected workflow schedule '{plan_res['goal']}' based on analytical objective.",
            reasoning=plan_res["reasoning"],
            confidence=plan_res["confidence"],
            findings=[],
            recommendations=[],
            tool_trace=[],
            execution_time_ms=execution_time_ms
        )

        # 6. Build execution trace log step
        execution_step = {
            "type": "agent_step",
            "trace_id": planner_trace_id,
            "parent_trace_id": root_trace_id,
            "agent": self.name,
            "tool": None,
            "status": "completed",
            "started_at": started_at_str,
            "completed_at": completed_at_str,
            "duration_ms": execution_time_ms,
            "confidence": plan_res["confidence"],
            "blackboard_version": 1
        }

        # 7. Telemetry blackboard_updated event
        blackboard_event = {
            "type": "telemetry_event",
            "event": "blackboard_updated",
            "agent_name": self.name,
            "timestamp": completed_at_str
        }

        # Register capabilities with the local Foundry adapter
        local_runtime_service.register_agent(self.name, {"type": "cognitive_planner", "version": "1.0"})
        local_runtime_service.publish_trace(planner_trace_id, execution_step)

        # Retrieve current execution log and append
        current_log = list(state.get("agent_execution_log") or [])
        current_log.append(execution_step)
        current_log.append(blackboard_event)

        # Accumulate memory entities in list
        memories = list(state.get("semantic_memories") or [])
        memories.append(memory_entity.model_dump())

        # Compile final updates for LangGraph AgentState blackboard
        updates = {
            "analysis_plan": plan_res,
            "workflow_steps": plan_res["workflow_steps"],
            "current_step": "Planner Complete",
            "planner_reasoning": plan_res["reasoning"],
            "planner_confidence": plan_res["confidence"],
            "current_agent": "planner",
            "planner_result": agent_result.model_dump(),
            "agent_execution_log": current_log,
            
            # Phase 5 additions
            "root_trace_id": root_trace_id,
            "semantic_goal": goal_entity.model_dump(),
            "semantic_dataset": dataset_entity.model_dump(),
            "semantic_memories": memories,
            "semantic_relationships": [r.model_dump() for r in relationships],
            
            "blackboard_version": 1,
            "blackboard_entity_count": 3 + len(column_entities),
            "blackboard_last_updated_by": self.name,
            "blackboard_last_trace_id": planner_trace_id
        }

        local_runtime_service.publish_memory(1, updates)
        self.run_telemetry_end(task_id, start_time, updates, tokens=120)
        return updates
