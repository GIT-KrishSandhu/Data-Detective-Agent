import pandas as pd
from typing import Dict, Any

def run_identifier_detector(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Pure Python/pandas tool to identify primary key/unique identifier columns in a DataFrame.
    An identifier column typically has 100% uniqueness (or close to it) and matches ID naming heuristics.
    """
    identifier_columns = []
    total_rows = len(df)
    if total_rows == 0:
        return {"identifier_columns": []}
        
    for col in df.columns:
        # Don't check empty or near-empty columns
        unique_count = df[col].nunique()
        if unique_count == 0:
            continue
            
        uniqueness_ratio = unique_count / total_rows
        
        # Check column name heuristics
        col_lower = col.lower()
        is_id_name = any(keyword in col_lower for keyword in ["id", "key", "code", "pk", "uuid", "guid"])
        
        # Check type
        is_float = pd.api.types.is_float_dtype(df[col])
        
        # Heuristic rules:
        if uniqueness_ratio == 1.0 and not is_float:
            reason = "100% unique values and not float type"
            if is_id_name:
                reason = "Contains ID keyword in name and has 100% unique values"
            identifier_columns.append({
                "column": col,
                "reason": reason,
                "uniqueness_ratio": uniqueness_ratio
            })
        elif is_id_name and uniqueness_ratio > 0.95 and not is_float:
            identifier_columns.append({
                "column": col,
                "reason": f"Contains ID keyword in name and has very high uniqueness ({uniqueness_ratio:.1%})",
                "uniqueness_ratio": uniqueness_ratio
            })
            
    return {
        "identifier_columns": identifier_columns
    }
