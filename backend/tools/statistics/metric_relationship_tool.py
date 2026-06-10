import pandas as pd
from typing import Dict, Any, List

def run_metric_relationship_tool(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluates numeric measures vs dimensions, classifying columns into roles
    and detailing groupings compatibility.
    """
    relationships = []
    columns = df.columns
    
    dimensions = []
    measures = []
    
    for col in columns:
        col_data = df[col].dropna()
        if len(col_data) == 0:
            continue
            
        is_numeric = pd.api.types.is_numeric_dtype(df[col])
        unique_ratio = col_data.nunique() / len(col_data) if len(col_data) > 0 else 0.0
        col_lower = col.lower()
        
        # Primary keys, strings, dates, and columns ending in keyword IDs are dimensions
        if not is_numeric or any(kw in col_lower for kw in ["id", "key", "pk", "code", "index", "date", "time"]) or unique_ratio == 1.0:
            dimensions.append(col)
        else:
            measures.append(col)
            
    for measure in measures:
        for dim in dimensions:
            col_data = df[dim].dropna()
            unique_count = col_data.nunique()
            if 1 < unique_count < 100:
                relationships.append({
                    "measure": measure,
                    "dimension": dim,
                    "analyzable": True,
                    "confidence": 0.95,
                    "reasoning": f"Measure '{measure}' can be aggregated across categoric dimension '{dim}' (which has {unique_count} unique values)."
                })
            elif unique_count == 1:
                relationships.append({
                    "measure": measure,
                    "dimension": dim,
                    "analyzable": False,
                    "confidence": 1.0,
                    "reasoning": f"Dimension '{dim}' has only 1 unique value. Grouping by this column will yield no variance."
                })
                
    return {
        "dimensions": dimensions,
        "measures": measures,
        "pairings": relationships
    }
