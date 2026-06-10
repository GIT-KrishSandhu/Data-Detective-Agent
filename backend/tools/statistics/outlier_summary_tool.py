import pandas as pd
from typing import Dict, Any

def run_outlier_summary_tool(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Counts outlier rows for numeric columns using the Interquartile Range (IQR) method.
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns
    outliers = {}
    
    for col in numeric_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            q1 = col_data.quantile(0.25)
            q3 = col_data.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outlier_mask = (col_data < lower_bound) | (col_data > upper_bound)
            count = int(outlier_mask.sum())
            ratio = float(count / len(col_data)) if len(col_data) > 0 else 0.0
            
            outliers[col] = {
                "outlier_count": count,
                "outlier_ratio": ratio,
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound)
            }
            
    return {"outliers": outliers}
