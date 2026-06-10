from services.microsoft.semantic_entities.semantic_entity import SemanticEntity

class BusinessMetricEntity(SemanticEntity):
    """
    Semantic Entity representing columns identified as key business metrics (KPIs or measures).
    """
    column_name: str
    metric_type: str  # e.g., 'Revenue', 'Cost', 'Sales', 'Profit', 'GeneralNumeric'
    is_aggregatable: bool
    default_aggregation: str  # e.g., 'Sum', 'Average', 'Median', 'None'
