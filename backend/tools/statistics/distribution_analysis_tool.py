import pandas as pd
from typing import Dict, Any
from tools.statistics.numeric_summary_tool import run_numeric_summary_tool

def run_distribution_analysis_tool(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluates the normality and skewness description of numeric columns.
    """
    summary_res = run_numeric_summary_tool(df)
    numeric_summary = summary_res.get("numeric_columns", {})
    distributions = {}
    
    for col, stats in numeric_summary.items():
        skew = stats["skew"]
        kurt = stats["kurt"]
        
        # normal distributions have skew near 0 and kurtosis near 0 (Fisher excess)
        is_normal = abs(skew) < 0.5 and abs(kurt) < 1.0
        
        if skew > 1.0:
            skew_desc = "Heavily right-skewed (positive skew)"
        elif skew < -1.0:
            skew_desc = "Heavily left-skewed (negative skew)"
        elif skew > 0.5:
            skew_desc = "Moderately right-skewed"
        elif skew < -0.5:
            skew_desc = "Moderately left-skewed"
        else:
            skew_desc = "Approximately symmetric"
            
        distributions[col] = {
            "is_normal": is_normal,
            "skewness_desc": skew_desc,
            "skew": skew,
            "kurtosis": kurt
        }
        
    return {"distributions": distributions}
