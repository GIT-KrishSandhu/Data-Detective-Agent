from services.microsoft.semantic_entities.semantic_entity import SemanticEntity
from typing import Dict, Any

class StatisticsEntity(SemanticEntity):
    """
    Semantic Entity containing dataset-wide structural profiling statistics.
    """
    row_count: int
    column_count: int
    numeric_columns_count: int
    categorical_columns_count: int
    datetime_columns_count: int
    constant_columns_count: int
    total_nulls: int
    average_null_percentage: float
    duplicate_rows: int
    outlier_count: int
