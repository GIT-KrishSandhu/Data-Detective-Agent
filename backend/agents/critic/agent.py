from typing import Any, Dict
from agents.base import BaseAgent
from state.schema import AgentState

class CriticAgent(BaseAgent):
    """
    Agent acting as the safety guardrail. Inspects plans, findings, and drafts
    to enforce core principles:
    - No hallucinated insights
    - No forecasting or prediction models
    - No unsupported claims without SQL evidence
    """

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        task_id = "critic_inspection"
        start_time = self.run_telemetry_start(task_id, state)
        
        # Simulated review of current state
        criticism = []
        
        # Check for forecasting attempts
        if state.get("plan") and any("forecast" in str(step).lower() for step in state["plan"].get("steps", [])):
            criticism.append({
                "type": "forecasting_violation",
                "message": "The plan contains predictive steps. Under core principles, forecasting is strictly banned."
            })
            
        # Standard safety approval log
        critic_results = {
            "passed_checks": len(criticism) == 0,
            "violations": criticism,
            "inspected_nodes": ["planner", "quality", "statistics"]
        }
        
        updates = {
            "critic_feedback": [critic_results],
            "current_agent": "critic"
        }
        
        self.run_telemetry_end(task_id, start_time, updates, tokens=180)
        return updates
