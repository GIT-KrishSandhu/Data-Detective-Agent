from services.microsoft.semantic_entities.semantic_entity import SemanticEntity
from typing import List

class QualityIssueEntity(SemanticEntity):
    """
    Semantic Entity representing a data quality defect discovered by the Quality Agent.
    """
    title: str
    description: str
    severity: str  # 'Info', 'Warning', 'Critical'
    affected_columns: List[str]
    evidence: str
    business_impact: str
