import os
from typing import Any, Dict, List, Tuple
import pandas as pd
import numpy as np

def clean_value_for_json(val: Any) -> Any:
    """
    Ensures that values extracted from pandas series (often numpy types)
    are converted to standard python types suitable for json serialization.
    """
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if isinstance(val, (pd.Timestamp, np.datetime64)):
        return val.isoformat()
    return str(val)

def infer_column_type(series: pd.Series) -> str:
    """
    Infers the schema type from a pandas series.
    Returns: 'integer', 'float', 'boolean', 'datetime', or 'string'.
    """
    # Drop nulls to evaluate actual content
    clean_series = series.dropna()
    if clean_series.empty:
        return "string"

    # 1. Check if datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    
    # If it is object/string, try to check if it represents dates
    if series.dtype == "object":
        # Heuristic: must look like a date (contains '-' or '/' or ':') to prevent random strings parsing
        sample_str = str(clean_series.iloc[0]).strip()
        if any(char in sample_str for char in ["-", "/", ":"]):
            try:
                # Use strict parse
                parsed = pd.to_datetime(clean_series.head(100), errors="raise")
                return "datetime"
            except (ValueError, TypeError, OverflowError):
                pass

    # 2. Check if boolean
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
        
    if series.dtype == "object":
        # Check if all clean values are in true/false terms
        string_vals = clean_series.astype(str).str.lower().str.strip()
        if string_vals.isin(["true", "false", "yes", "no", "y", "n"]).all():
            return "boolean"

    # 3. Check if integer
    if pd.api.types.is_integer_dtype(series):
        return "integer"

    # 4. Check if float
    if pd.api.types.is_float_dtype(series):
        # Double check if all values are actually integers represented as floats (e.g. 1.0, 2.0)
        # Check if non-null elements equal their integer casting
        if (clean_series % 1 == 0).all():
            return "integer"
        return "float"

    # 5. Try converting object type to numbers
    if series.dtype == "object":
        try:
            converted = pd.to_numeric(clean_series, errors="raise")
            if (converted % 1 == 0).all():
                return "integer"
            return "float"
        except (ValueError, TypeError):
            pass

    # Fallback to string
    return "string"

def inspect_dataset_file(file_path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Reads CSV or XLSX dataset and performs metadata, schema, and preview extraction.
    Returns: (metadata, schema_info, preview_data)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[-1].lower()
    
    # Read file based on extension
    if ext == ".csv":
        try:
            # First try utf-8
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            # Fallback to standard Windows latin encodings
            df = pd.read_csv(file_path, encoding="cp1252")
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    row_count = len(df)
    column_count = len(df.columns)
    file_size = os.path.getsize(file_path)

    # 1. Compile Metadata
    metadata = {
        "filename": os.path.basename(file_path),
        "file_size_bytes": file_size,
        "row_count": row_count,
        "column_count": column_count,
        "detected_type": ext.lstrip(".")
    }

    # 2. Compile Schema Information
    schema_info = []
    inferred_types_map = {}
    
    for col_name in df.columns:
        series = df[col_name]
        col_type = infer_column_type(series)
        inferred_types_map[str(col_name)] = col_type

        null_count = int(series.isna().sum())
        null_percentage = float(null_count / row_count) if row_count > 0 else 0.0
        unique_values = int(series.nunique(dropna=True))

        # Sample values: take up to 5 unique non-null values
        unique_non_nulls = series.dropna().unique()
        sample_vals = [clean_value_for_json(v) for v in unique_non_nulls[:5]]

        schema_info.append({
            "name": str(col_name),
            "inferred_type": col_type,
            "null_count": null_count,
            "null_percentage": round(null_percentage, 4),
            "unique_values": unique_values,
            "sample_values": sample_vals
        })

    # 3. Compile Preview Data (Top 20 rows)
    preview_df = df.head(20)
    preview_rows = []
    
    for idx, row in preview_df.iterrows():
        row_dict = {}
        for col_name in df.columns:
            row_dict[str(col_name)] = clean_value_for_json(row[col_name])
        preview_rows.append(row_dict)

    preview_data = {
        "columns": [str(c) for c in df.columns],
        "inferred_types": inferred_types_map,
        "rows": preview_rows
    }

    return metadata, schema_info, preview_data
