from typing import Dict, Any
# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, END
# pyrefly: ignore [missing-import]
from langchain_core.language_models.chat_models import BaseChatModel

from state.schema import AgentState
from agents.planner.planner_agent import PlannerAgent
from agents.quality.quality_agent import QualityAgent
from agents.bi_readiness.bi_readiness_agent import BIReadinessAgent
from agents.evaluation import EvaluationAgent

def build_agent_graph(llm: BaseChatModel) -> StateGraph:
    """
    Builds the planning execution pipeline graph using LangGraph.
    Establishes state transitions, routing, and blackboard operations.
    
    Current Layout:
    START -> Planner -> Quality -> BI Readiness -> Evaluation -> END
    """
    
    # Initialize agents with provider-agnostic LLM
    planner = PlannerAgent(name="PlannerAgent", llm=llm, system_prompt="You plan data audits.")
    quality = QualityAgent(name="QualityAgent", llm=llm, system_prompt="You run data quality audits.")
    bi_readiness = BIReadinessAgent(name="BIReadinessAgent", llm=llm, system_prompt="You audit dataset structures for Power BI readiness.")
    evaluation = EvaluationAgent(name="EvaluationAgent", llm=llm, system_prompt="You evaluate execution quality metrics.")

    # Instantiate LangGraph StateGraph
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("planner", planner.execute)
    workflow.add_node("quality", quality.execute)
    workflow.add_node("bi_readiness", bi_readiness.execute)
    workflow.add_node("evaluation", evaluation.execute)

    # Establish edges (Standard workflow routing)
    workflow.set_entry_point("planner")
    
    # Route planner -> quality -> bi_readiness -> evaluation -> END
    workflow.add_edge("planner", "quality")
    workflow.add_edge("quality", "bi_readiness")
    workflow.add_edge("bi_readiness", "evaluation")
    workflow.add_edge("evaluation", END)

    # Compile the graph
    return workflow.compile()


