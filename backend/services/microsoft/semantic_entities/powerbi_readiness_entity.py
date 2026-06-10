from services.microsoft.semantic_entities.semantic_entity import SemanticEntity
from typing import Dict, Any, List

class PowerBIReadinessEntity(SemanticEntity):
    """
    Semantic Entity holding the Power BI readiness scorecards, ratings, and star schema suggestions.
    """
    readiness_score: int  # 0-100
    category_ratings: Dict[str, float]  # e.g., {'schema': 5.0, 'quality': 3.0, 'relationships': 5.0}
    overall_rating_text: str  # e.g., 'ENTERPRISE READY', 'NEEDS ATTENTION', 'FAIL'
    star_schema_suggestions: Dict[str, Any]  # e.g., {'dimension_tables': [], 'fact_tables': [], 'reasoning': ''}
    business_recommendations: List[str]
