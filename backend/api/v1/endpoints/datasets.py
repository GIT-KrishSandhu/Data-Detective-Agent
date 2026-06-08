import os
from typing import Dict, Any, List
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd

from database.session import get_db
from services.datasets.service import dataset_service
from schemas.dataset import DatasetResponse, DatasetPreview, ColumnSchema

router = APIRouter()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a CSV or XLSX dataset (Max 50MB).
    Triggers the schema discovery engine and persists metadata.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty."
        )

    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file extension. Only CSV and XLSX (.csv, .xlsx, .xls) are permitted."
        )

    # Validate file size
    try:
        contents = await file.read()
        file_size = len(contents)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds the maximum limit of 50 MB (uploaded {file_size / (1024*1024):.2f} MB)."
            )
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading upload stream: {str(e)}"
        )

    # Process and save file
    try:
        db_dataset = await dataset_service.save_uploaded_file(
            db=db,
            filename=file.filename,
            file_content=contents
        )
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file contains no readable columns or rows."
        )
    except (pd.errors.ParserError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Malformed spreadsheet content: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database or discovery engine failure: {str(e)}"
        )

    # Map database model to Pydantic schema response
    return DatasetResponse(
        dataset_id=db_dataset.id,
        metadata={
            "filename": db_dataset.filename,
            "file_size_bytes": db_dataset.file_size,
            "row_count": db_dataset.row_count,
            "column_count": db_dataset.column_count,
            "detected_type": db_dataset.detected_type,
            "file_hash": db_dataset.file_hash,
            "profile_summary": db_dataset.profile_summary,
            "analysis_goal": db_dataset.analysis_goal
        },
        schema_info=db_dataset.schema_info,
        preview_data=db_dataset.preview_data,
        created_at=db_dataset.created_at
    )

@router.get("/{dataset_id}/preview", response_model=DatasetPreview)
async def get_preview(
    dataset_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch the cached top 20 rows preview of the dataset.
    """
    db_dataset = await dataset_service.get_dataset(db, dataset_id)
    if not db_dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID '{dataset_id}' not found."
        )
    return db_dataset.preview_data

@router.get("/{dataset_id}/schema", response_model=List[ColumnSchema])
async def get_schema(
    dataset_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch the inferred type schema and null analysis of the dataset columns.
    """
    db_dataset = await dataset_service.get_dataset(db, dataset_id)
    if not db_dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID '{dataset_id}' not found."
        )
    return db_dataset.schema_info

@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch the complete dataset metadata record by UUID.
    """
    db_dataset = await dataset_service.get_dataset(db, dataset_id)
    if not db_dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID '{dataset_id}' not found."
        )
    return DatasetResponse(
        dataset_id=db_dataset.id,
        metadata={
            "filename": db_dataset.filename,
            "file_size_bytes": db_dataset.file_size,
            "row_count": db_dataset.row_count,
            "column_count": db_dataset.column_count,
            "detected_type": db_dataset.detected_type,
            "file_hash": db_dataset.file_hash,
            "profile_summary": db_dataset.profile_summary,
            "analysis_goal": db_dataset.analysis_goal
        },
        schema_info=db_dataset.schema_info,
        preview_data=db_dataset.preview_data,
        created_at=db_dataset.created_at
    )
