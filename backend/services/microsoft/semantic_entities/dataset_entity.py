from pydantic import BaseModel, Field
from services.microsoft.semantic_entities.semantic_entity import SemanticEntity
from typing import List, Any, Dict

class ColumnEntity(BaseModel):
    """
    Sub-model representing column details and schema constraints.
    """
    name: str
    inferred_type: str
    null_count: int
    null_percentage: float
    unique_values: int
    sample_values: List[Any] = Field(default_factory=list)

class DatasetEntity(SemanticEntity):
    """
    Semantic Entity representing the ingested dataset metadata and schema.
    """
    filename: str
    file_path: str
    file_size_bytes: int
    row_count: int
    column_count: int
    detected_type: str
    columns: List[ColumnEntity] = Field(default_factory=list)
