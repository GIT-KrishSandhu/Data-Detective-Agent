from services.microsoft.semantic_entities.semantic_entity import SemanticEntity

class AggregationRecommendationEntity(SemanticEntity):
    """
    Semantic Entity suggesting aggregation recommendations for columns (e.g. median KPI vs dimension lookup).
    """
    column_name: str
    recommended_aggregation: str  # e.g., 'Sum', 'Average', 'Median', 'None'
    reasoning: str
