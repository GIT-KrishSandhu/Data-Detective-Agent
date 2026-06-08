from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.language_models.chat_models import BaseChatModel

from state.schema import AgentState
from agents.planner.planner_agent import PlannerAgent

def build_agent_graph(llm: BaseChatModel) -> StateGraph:
    """
    Builds the planning execution pipeline graph using LangGraph.
    Establishes state transitions, routing, and blackboard operations.
    
    Current Layout:
    START -> Planner -> END
    
    To scale in future phases, register new nodes (e.g. quality, statistics)
    and chain them after 'planner' node.
    """
    
    # Initialize agents with provider-agnostic LLM
    planner = PlannerAgent(name="PlannerAgent", llm=llm, system_prompt="You plan data audits.")

    # Instantiate LangGraph StateGraph
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("planner", planner.execute)

    # Register future node placeholders easily here:
    # workflow.add_node("quality", quality.execute)
    # workflow.add_node("statistics", statistics.execute)

    # Establish edges (Standard workflow routing)
    workflow.set_entry_point("planner")
    
    # Current scaffolding ends immediately after planning.
    # In future phases, route 'planner' -> 'quality' -> ... -> END
    workflow.add_edge("planner", END)

    # Compile the graph
    return workflow.compile()
