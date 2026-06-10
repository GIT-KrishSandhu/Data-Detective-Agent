from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Any, Dict
from datetime import datetime, timezone

class SemanticEntity(BaseModel):
    """
    Base class representing a typed, traceable object stored on the Shared Blackboard.
    Enforces trace audits, agent origin mapping, and confidence scoring.
    """
    entity_id: str
    entity_type: str
    created_by_agent: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: float = 1.0
    dependencies: List[str] = Field(default_factory=list)
    
    # Phase 6 additions
    id: Optional[str] = None
    trace_id: Optional[str] = None
    relationships: List[Dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def set_id_from_entity_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "entity_id" in data and ("id" not in data or data["id"] is None):
                data["id"] = data["entity_id"]
            elif "id" in data and ("entity_id" not in data or data["entity_id"] is None):
                data["entity_id"] = data["id"]
        return data

