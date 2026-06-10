import pandas as pd
from typing import Dict, Any

def run_missing_value_tool(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Pure Python/pandas tool to scan a DataFrame for missing/null values.
    Returns completeness metrics for each column and overall.
    """
    total_rows = len(df)
    columns_info = {}
    total_missing = 0
    
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_percentage = float(null_count / total_rows) if total_rows > 0 else 0.0
        total_missing += null_count
        columns_info[col] = {
            "null_count": null_count,
            "null_percentage": null_percentage
        }
        
    return {
        "columns": columns_info,
        "total_missing": total_missing,
        "total_rows": total_rows
    }
