from services.microsoft.semantic_entities.semantic_entity import SemanticEntity
from typing import Optional

class AnalysisGoalEntity(SemanticEntity):
    """
    Semantic Entity representing the user's analytical goal.
    """
    goal_text: str
    target_metric: Optional[str] = None
    priority_level: str = "Medium"  # 'Low', 'Medium', 'High', 'Critical'
