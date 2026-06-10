from services.microsoft.semantic_entities.semantic_entity import SemanticEntity

class DistributionEntity(SemanticEntity):
    """
    Semantic Entity containing column-level metrics such as mean, median, skewness, and outliers.
    """
    column_name: str
    mean: float
    median: float
    min_val: float
    max_val: float
    std_dev: float
    skewness: float
    kurtosis: float
    outlier_count: int
    is_normal: bool
    skewness_interpretation: str
