from typing import Any, Dict, List
import pandas as pd
from tools.schema_inspector import infer_column_type

def calculate_profile_summary(df: pd.DataFrame) -> Dict[str, int]:
    """
    Deterministically calculates column category distributions and null rates.
    This runs entirely locally using Pandas, with zero LLM requirements.
    
    Returns:
        Dict[str, int]: {
            "numeric_columns": int,
            "categorical_columns": int,
            "datetime_columns": int,
            "boolean_columns": int,
            "columns_with_missing_values": int
        }
    """
    numeric_count = 0
    categorical_count = 0
    datetime_count = 0
    boolean_count = 0
    missing_val_cols = 0

    for col in df.columns:
        series = df[col]
        # Check missing values
        null_count = int(series.isna().sum())
        if null_count > 0:
            missing_val_cols += 1

        # Check inferred column type
        inferred = infer_column_type(series)
        
        if inferred in ["integer", "float"]:
            numeric_count += 1
        elif inferred == "datetime":
            datetime_count += 1
        elif inferred == "boolean":
            boolean_count += 1
        else: # string / object fallback
            categorical_count += 1

    return {
        "numeric_columns": numeric_count,
        "categorical_columns": categorical_count,
        "datetime_columns": datetime_count,
        "boolean_columns": boolean_count,
        "columns_with_missing_values": missing_val_cols
    }
