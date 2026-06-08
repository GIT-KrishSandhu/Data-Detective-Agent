from typing import Any, Dict
from agents.base import BaseAgent
from state.schema import AgentState

class CleaningAgent(BaseAgent):
    """
    Agent responsible for designing cleaning policies and suggesting actions.
    Every recommendation is stored for human-in-the-loop review.
    No modifications are executed without human verification.
    """

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        task_id = "cleaning_suggestions"
        start_time = self.run_telemetry_start(task_id, state)
        
        # Simulated suggestions
        suggested_actions = [
            {
                "id": "action_001",
                "field": "Age",
                "issue": "Negative numbers",
                "resolution": "Set negative age values to NULL or drop corresponding records",
                "scope_affected_rows": 2,
                "code_preview": "df.loc[df['Age'] < 0, 'Age'] = None"
            },
            {
                "id": "action_002",
                "field": "revenue",
                "issue": "Missing values",
                "resolution": "Impute missing revenue fields using the median value (99.00) or leave as NULL",
                "scope_affected_rows": 2,
                "code_preview": "df['revenue'] = df['revenue'].fillna(99.00)"
            }
        ]
        
        updates = {
            "suggested_cleaning_actions": suggested_actions,
            "cleaning_applied": False,
            "current_agent": "cleaning"
        }
        
        self.run_telemetry_end(task_id, start_time, updates, tokens=200)
        return updates
