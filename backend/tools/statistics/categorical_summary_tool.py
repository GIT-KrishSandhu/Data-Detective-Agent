import pandas as pd
from typing import Dict, Any

def run_categorical_summary_tool(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Summarizes unique counts, cardinality ratios, and modes for non-numeric columns.
    """
    non_numeric_cols = df.select_dtypes(exclude=["number"]).columns
    summary = {}
    
    for col in non_numeric_cols:
        col_data = df[col].dropna()
        total_count = len(col_data)
        if total_count > 0:
            unique_count = int(col_data.nunique())
            ratio = float(unique_count / total_count)
            top_val = col_data.mode().iloc[0] if not col_data.mode().empty else None
            top_count = int((col_data == top_val).sum()) if top_val is not None else 0
            
            summary[col] = {
                "unique_count": unique_count,
                "cardinality_ratio": ratio,
                "most_frequent_value": str(top_val) if top_val is not None else None,
                "most_frequent_count": top_count
            }
            
    return {"categorical_columns": summary}
