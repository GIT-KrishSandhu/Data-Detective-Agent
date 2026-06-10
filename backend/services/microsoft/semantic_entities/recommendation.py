from services.microsoft.semantic_entities.semantic_entity import SemanticEntity
from typing import List

class RecommendationEntity(SemanticEntity):
    """
    Semantic Entity representing suggestions to address blackboard issues.
    """
    recommendation_text: str
    actionable_steps: List[str]
