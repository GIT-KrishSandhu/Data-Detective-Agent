from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ColumnSchema(BaseModel):
    name: str = Field(..., description="The name of the column.")
    inferred_type: str = Field(..., description="The inferred data type: integer, float, string, boolean, or datetime.")
    null_count: int = Field(..., description="Total count of missing/null values.")
    null_percentage: float = Field(..., description="Percentage of missing/null values.")
    unique_values: int = Field(..., description="Total count of unique values in the column.")
    sample_values: List[Any] = Field(..., description="A short list of sample values from the column.")

class ProfileSummarySchema(BaseModel):
    numeric_columns: int = Field(..., description="Count of numeric columns (integer, float).")
    categorical_columns: int = Field(..., description="Count of categorical/string columns.")
    datetime_columns: int = Field(..., description="Count of datetime columns.")
    boolean_columns: int = Field(..., description="Count of boolean columns.")
    columns_with_missing_values: int = Field(..., description="Count of columns containing missing/null values.")

class DatasetMetadata(BaseModel):
    filename: str = Field(..., description="Name of the uploaded spreadsheet.")
    file_size_bytes: int = Field(..., description="The size of the spreadsheet in bytes.")
    row_count: int = Field(..., description="Total number of rows detected.")
    column_count: int = Field(..., description="Total number of columns detected.")
    detected_type: str = Field(..., description="Spreadsheet extension type: csv or xlsx.")
    file_hash: str = Field(..., description="SHA256 checksum identifying the file content.")
    profile_summary: ProfileSummarySchema = Field(..., description="Count details by column category.")
    analysis_goal: Optional[str] = Field(None, description="The selected analysis goal.")

class DatasetPreview(BaseModel):
    columns: List[str] = Field(..., description="List of all column headers in visual order.")
    inferred_types: Dict[str, str] = Field(..., description="Column data types lookup mapping.")
    rows: List[Dict[str, Any]] = Field(..., description="Top 20 data rows of the spreadsheet.")

class DatasetResponse(BaseModel):
    dataset_id: str = Field(..., description="Unique UUID identifying the uploaded dataset.")
    metadata: DatasetMetadata = Field(..., description="Dataset high-level statistics and metadata.")
    schema_info: List[ColumnSchema] = Field(..., description="Parsed columns structure and statistical type details.")
    preview_data: DatasetPreview = Field(..., description="First 20 rows of headers + records.")
    created_at: datetime
