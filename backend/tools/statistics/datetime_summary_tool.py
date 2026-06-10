import pandas as pd
from typing import Dict, Any

def run_datetime_summary_tool(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Identifies datetime columns, checks their spans, and computes continuity ratios.
    """
    summary = {}
    
    for col in df.columns:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            is_dt = pd.api.types.is_datetime64_any_dtype(df[col])
            if not is_dt:
                # Check for date keyword or test conversion on a small slice
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ["date", "time", "timestamp", "year", "month"]):
                    try:
                        sample = col_data.head(5)
                        pd.to_datetime(sample, errors="raise")
                        is_dt = True
                    except (ValueError, TypeError):
                        is_dt = False
            
            if is_dt:
                try:
                    dt_series = pd.to_datetime(df[col], errors="coerce").dropna()
                    if len(dt_series) > 0:
                        min_date = dt_series.min()
                        max_date = dt_series.max()
                        
                        days_diff = (max_date - min_date).days
                        unique_dates_count = dt_series.dt.date.nunique()
                        continuity_ratio = float(unique_dates_count / (days_diff + 1)) if days_diff > 0 else 1.0
                        
                        summary[col] = {
                            "min_date": min_date.isoformat(),
                            "max_date": max_date.isoformat(),
                            "span_days": days_diff,
                            "unique_dates": unique_dates_count,
                            "continuity_ratio": min(1.0, continuity_ratio)
                        }
                except Exception:
                    pass
                    
    return {"datetime_columns": summary}
