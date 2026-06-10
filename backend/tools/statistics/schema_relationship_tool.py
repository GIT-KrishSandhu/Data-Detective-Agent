import pandas as pd
from typing import Dict, Any, List

def run_schema_relationship_tool(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Identifies primary/foreign key candidates to suggest star schema layouts.
    """
    primary_keys = []
    foreign_keys = []
    
    for col in df.columns:
        col_data = df[col].dropna()
        if len(col_data) == 0:
            continue
            
        col_lower = col.lower()
        unique_ratio = col_data.nunique() / len(col_data) if len(col_data) > 0 else 0.0
        
        if unique_ratio == 1.0 and any(kw in col_lower for kw in ["id", "key", "pk"]):
            primary_keys.append(col)
        elif unique_ratio < 1.0 and any(kw in col_lower for kw in ["id", "key"]):
            foreign_keys.append(col)
            
    dim_candidates = []
    fact_candidates = []
    
    for pk in primary_keys:
        clean_name = pk
        for kw in ["id", "key", "pk", "_id", "_key", "ID", "Key", "PK"]:
            clean_name = clean_name.replace(kw, "")
        if not clean_name:
            clean_name = "Primary"
        dim_candidates.append({
            "table_name": clean_name,
            "pk": pk
        })
        
    has_measures = any(
        pd.api.types.is_numeric_dtype(df[col]) and col not in primary_keys
        for col in df.columns
    )
    if has_measures or len(foreign_keys) > 0:
        fact_candidates.append({
            "table_name": "FactTable",
            "fks": foreign_keys,
            "measures": [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c not in primary_keys and not any(k in c.lower() for k in ["id", "key"])]
        })
        
    return {
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "dim_candidates": dim_candidates,
        "fact_candidates": fact_candidates
    }
