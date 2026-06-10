import pandas as pd
from typing import Dict, Any

def run_high_cardinality_detector(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Pure Python/pandas tool to check categorical/object columns for high cardinality.
    High cardinality in categories makes grouping or statistical encoding complex and noisy.
    """
    high_cardinality_columns = []
    total_rows = len(df)
    if total_rows == 0:
        return {"high_cardinality_columns": []}
        
    for col in df.columns:
        # We only check categorical or object (text) columns
        if not (pd.api.types.is_object_dtype(df[col]) or isinstance(df[col].dtype, pd.CategoricalDtype)):
            continue
            
        unique_count = df[col].nunique()
        cardinality_ratio = unique_count / total_rows
        
        # High cardinality threshold criteria:
        # - More than 10 unique values
        # - Either the unique count is > 50 and uniqueness ratio is > 10%, OR the ratio is > 50%
        if unique_count > 10 and (cardinality_ratio > 0.50 or (unique_count > 50 and cardinality_ratio > 0.10)):
            high_cardinality_columns.append({
                "column": col,
                "unique_count": unique_count,
                "cardinality_ratio": cardinality_ratio
            })
            
    return {
        "high_cardinality_columns": high_cardinality_columns
    }
