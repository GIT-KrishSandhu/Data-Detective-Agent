import pandas as pd
from typing import Dict, Any

def run_numeric_summary_tool(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes basic summary statistics for all numeric columns in a DataFrame.
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns
    summary = {}
    for col in numeric_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            summary[col] = {
                "mean": float(col_data.mean()),
                "median": float(col_data.median()),
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "std": float(col_data.std()) if len(col_data) > 1 else 0.0,
                "skew": float(col_data.skew()) if len(col_data) > 2 else 0.0,
                "kurt": float(col_data.kurt()) if len(col_data) > 3 else 0.0
            }
    return {"numeric_columns": summary}
