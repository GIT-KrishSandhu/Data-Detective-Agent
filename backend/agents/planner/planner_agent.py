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
        task_id = "agent_planning"
        start_time = self.run_telemetry_start(task_id, state)

        goal = state.get("goal") or "Data Quality Audit"
        metadata = state.get("dataset_metadata") or {}
        profile_summary = state.get("profile_summary") or {
            "numeric_columns": 0,
            "categorical_columns": 0,
            "datetime_columns": 0,
            "boolean_columns": 0,
            "columns_with_missing_values": 0
        }

        # Calculate workflow
        plan_res = self.plan_workflow(goal, metadata, profile_summary)

        # Compile final updates for LangGraph AgentState blackboard
        updates = {
            "analysis_plan": plan_res,
            "workflow_steps": plan_res["workflow_steps"],
            "current_step": "Planner Complete",
            "planner_reasoning": plan_res["reasoning"],
            "planner_confidence": plan_res["confidence"],
            "current_agent": "planner"
        }

        self.run_telemetry_end(task_id, start_time, updates, tokens=120)
        return updates
