from pydantic import BaseModel, Field
from datetime import datetime, timezone

class SemanticRelationship(BaseModel):
    """
    Semantic model representing typed relationships between entities or agents.
    Supports constructs like 'contains', 'has', 'generates', 'belongs_to', and 'creates'.
    """
    relationship_id: str
    source_id: str
    target_id: str
    relationship_type: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
