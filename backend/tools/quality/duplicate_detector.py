import pandas as pd
from typing import Dict, Any

def run_duplicate_detector(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Pure Python/pandas tool to check a DataFrame for duplicate rows.
    """
    total_rows = len(df)
    duplicate_count = int(df.duplicated().sum())
    duplicate_percentage = float(duplicate_count / total_rows) if total_rows > 0 else 0.0
    
    return {
        "duplicate_rows_count": duplicate_count,
        "duplicate_percentage": duplicate_percentage,
        "total_rows": total_rows
    }
