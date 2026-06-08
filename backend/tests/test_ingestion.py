import io
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from main import app
from database.session import get_db

# Create test client
client = TestClient(app)

# Mock database dependency
async def override_get_db():
    db = AsyncMock()
    yield db

app.dependency_overrides[get_db] = override_get_db

def test_upload_invalid_file_type():
    """
    Test uploading an invalid file extension (e.g. .txt).
    Should return 400 Bad Request.
    """
    file_content = b"sample text data"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    
    response = client.post("/api/v1/datasets/upload", files=files)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unsupported file extension" in response.json()["detail"]

def test_upload_oversized_file():
    """
    Test uploading a file larger than 50MB.
    Should return 400 Bad Request.
    """
    # 51 MB of mock data
    oversized_content = b"0" * (51 * 1024 * 1024)
    files = {"file": ("test.csv", io.BytesIO(oversized_content), "text/csv")}
    
    response = client.post("/api/v1/datasets/upload", files=files)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "File size exceeds the maximum limit" in response.json()["detail"]

def test_upload_empty_file():
    """
    Test uploading an empty file (0 bytes).
    Should return 400 Bad Request.
    """
    files = {"file": ("test.csv", io.BytesIO(b""), "text/csv")}
    
    response = client.post("/api/v1/datasets/upload", files=files)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Uploaded file is empty" in response.json()["detail"]

def test_upload_malformed_csv():
    """
    Test uploading a malformed CSV file.
    Should return 400 Bad Request due to pandas parsing errors.
    """
    # CSV with uneven row structures and invalid quoting to trigger ParserError
    malformed_csv = b'name,age\n"Alice",30,extra_column_error\n"Bob",25\n"Charlie"\n'
    # Wait, pandas read_csv actually parses uneven columns by adding columns or filling NaNs,
    # unless it has severe token errors (like unmatched quotes). Let's pass a truly broken quote CSV:
    malformed_csv = b'col1,col2\n"unclosed quote,value2\n'
    
    files = {"file": ("broken.csv", io.BytesIO(malformed_csv), "text/csv")}
    
    # We patch dataset_service.save_uploaded_file to verify it parses and correctly raises validation errors
    # or handle the call normally.
    response = client.post("/api/v1/datasets/upload", files=files)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Malformed spreadsheet" in response.json()["detail"] or "ParserError" in response.json()["detail"]

@pytest.mark.anyio
async def test_dataset_timezone_compatibility_real_db():
    """
    Regression test: Verifies that inserting a DatasetModel with a timezone-aware
    created_at datetime into the database does not raise any exceptions
    and correctly stores/retrieves timezone information.
    """
    from database.session import SessionLocal
    from models.dataset import DatasetModel
    from datetime import datetime, timezone
    import uuid
    from sqlalchemy.future import select

    async with SessionLocal() as session:
        test_id = str(uuid.uuid4())
        db_dataset = DatasetModel(
            id=test_id,
            filename="timezone_test.csv",
            file_path="dummy_path",
            file_size=123,
            detected_type="csv",
            row_count=10,
            column_count=2,
            analysis_goal="Test",
            file_hash="dummy_hash",
            profile_summary={"numeric_columns": 1, "categorical_columns": 1, "datetime_columns": 0, "boolean_columns": 0, "columns_with_missing_values": 0},
            schema_info=[{"name": "col1", "inferred_type": "integer", "null_count": 0, "null_percentage": 0.0, "unique_values": 10, "sample_values": [1]}],
            preview_data={"columns": ["col1"], "inferred_types": {"col1": "integer"}, "rows": []},
            created_at=datetime.now(timezone.utc)
        )
        try:
            session.add(db_dataset)
            await session.commit()
            
            # Fetch it back and assert timezone information is present
            result = await session.execute(select(DatasetModel).where(DatasetModel.id == test_id))
            retrieved = result.scalar_one()
            
            assert retrieved.created_at is not None
            assert retrieved.created_at.tzinfo is not None
            assert retrieved.created_at.tzinfo.utcoffset(retrieved.created_at) is not None
            
        finally:
            # Clean up
            await session.delete(db_dataset)
            await session.commit()
