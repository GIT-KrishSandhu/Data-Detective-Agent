from typing import Any, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    State definition for the Data Detective Agent LangGraph multi-agent system.
    This maintains the coordinate blackboard state that is passed between
    independent agent nodes, storing intermediate evidence, plans, and reports.
    """

    # Input dataset metadata
    dataset_path: str
    goal: str  # quality, eda, summary, powerbi
    schema_info: Dict[str, Any]

    # Ingestion pipeline additions
    dataset_id: Optional[str]
    dataset_metadata: Optional[Dict[str, Any]]
    dataset_schema: Optional[List[Dict[str, Any]]]
    dataset_preview: Optional[Dict[str, Any]]

    # Phase 3 workflow state variables
    analysis_goal: Optional[str]
    profile_summary: Optional[Dict[str, int]]
    analysis_plan: Optional[Dict[str, Any]]
    workflow_steps: Optional[List[str]]
    current_step: Optional[str]
    planner_reasoning: Optional[str]
    planner_confidence: Optional[float]

    # Shared execution variables
    messages: List[BaseMessage]
    current_agent: str
    errors: List[str]

    # Node output storage (Blackboard architecture pattern)
    plan: Optional[Dict[str, Any]]
    quality_report: Optional[Dict[str, Any]]
    statistical_summary: Optional[Dict[str, Any]]
    charts: Optional[List[Dict[str, Any]]]
    
    # Cleaning actions and human approval structure
    suggested_cleaning_actions: Optional[List[Dict[str, Any]]]
    user_approved_cleaning_actions: Optional[List[Dict[str, Any]]]
    cleaning_applied: bool

    # Evaluation, Critique & Verification
    critic_feedback: Optional[List[Dict[str, Any]]]
    validation_results: Optional[Dict[str, Any]]
    
    # Final generated artifacts
    final_report: Optional[str]  # Markdown string
    final_dataset_path: Optional[str]
