import pandas as pd
from typing import Dict, Any

def run_mixed_type_detector(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Pure Python/pandas tool to check a DataFrame for mixed-type columns.
    A column has mixed types if it contains non-null elements of different Python types.
    """
    mixed_type_columns = {}
    for col in df.columns:
        # Drop null values to check the type of actual values
        non_nulls = df[col].dropna()
        if len(non_nulls) == 0:
            continue
            
        # Extract name of type for each value
        type_names = non_nulls.map(lambda x: type(x).__name__)
        types_found = type_names.unique()
        
        if len(types_found) > 1:
            counts = type_names.value_counts()
            mixed_type_columns[col] = {
                "types_found": list(types_found),
                "type_counts": {str(k): int(v) for k, v in counts.items()}
            }
            
    return {
        "mixed_type_columns": mixed_type_columns
    }
