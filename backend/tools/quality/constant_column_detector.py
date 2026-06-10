import pandas as pd
from typing import Dict, Any

def run_constant_column_detector(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Pure Python/pandas tool to check a DataFrame for constant columns.
    A column is constant if it contains only a single unique value.
    """
    constant_columns = []
    for col in df.columns:
        unique_vals = df[col].nunique(dropna=True)
        if unique_vals == 1:
            # Get the single value
            val = df[col].dropna().iloc[0]
            # Convert numpy types to native Python types
            if hasattr(val, "item"):
                val = val.item()
            constant_columns.append({
                "column": col,
                "value": val
            })
        elif unique_vals == 0 and len(df) > 0:
            # All values in column are null
            constant_columns.append({
                "column": col,
                "value": None
            })
            
    return {
        "constant_columns": constant_columns
    }
