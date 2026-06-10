from pydantic import BaseModel, Field
from typing import List

class QualityFinding(BaseModel):
    """
    Typed data model representing a specific data quality issue discovered in the dataset.
    Features detailed evidence, specific business impacts, and actionable recommendations.
    """
    id: str
    title: str
    description: str
    severity: str  # 'Critical', 'Warning', 'Info'
    affected_columns: List[str] = Field(default_factory=list)
    evidence: str
    business_impact: str
    recommendation: str
    confidence: float
