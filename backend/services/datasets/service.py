import os
import uuid
import hashlib
import io
import pandas as pd
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.dataset import DatasetModel
from tools.schema_inspector import inspect_dataset_file
from tools.profile_summary import calculate_profile_summary

# Local storage path configuration
STORAGE_DIR = os.path.join(os.getcwd(), "storage", "datasets")
os.makedirs(STORAGE_DIR, exist_ok=True)

class DatasetService:
    """
    Dataset Service responsible for file storage management,
    SQLAlchemy database session execution, type profile calculations,
    and workflow goal updates.
    """

    async def save_uploaded_file(
        self, 
        db: AsyncSession, 
        filename: str, 
        file_content: bytes
    ) -> DatasetModel:
        """
        Saves the file to local disk, runs schema discovery,
        computes SHA256 file hashes, and records it in the database.
        """
        # 1. Calculate file SHA256 hash
        file_hash = hashlib.sha256(file_content).hexdigest()

        # 2. Parse file into Pandas DataFrame in-memory to compute profile summary
        ext = os.path.splitext(filename)[-1].lower()
        if ext == ".csv":
            try:
                df = pd.read_csv(io.BytesIO(file_content))
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(file_content), encoding="cp1252")
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        profile_summary = calculate_profile_summary(df)

        # 3. Generate unique UUID identification
        dataset_id = str(uuid.uuid4())
        sanitized_filename = "".join(c for c in filename if c.isalnum() or c in (".", "_", "-"))
        disk_filename = f"{dataset_id}_{sanitized_filename}"
        file_path = os.path.join(STORAGE_DIR, disk_filename)

        # 4. Write file stream to local storage
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        try:
            # 5. Extract metadata, schema mapping, and preview rows
            metadata, schema_info, preview_data = inspect_dataset_file(file_path)

            # 6. Create database persistence record
            db_dataset = DatasetModel(
                id=dataset_id,
                filename=metadata["filename"],
                file_path=file_path,
                file_size=metadata["file_size_bytes"],
                detected_type=metadata["detected_type"],
                row_count=metadata["row_count"],
                column_count=metadata["column_count"],
                analysis_goal=None,
                file_hash=file_hash,
                profile_summary=profile_summary,
                schema_info=schema_info,
                preview_data=preview_data
            )
            
            db.add(db_dataset)
            await db.flush()  # Populates id and created_at fields in context
            await db.commit()
            
            return db_dataset

        except Exception as e:
            # Clean up local file in case of validation/parsing errors
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e

    async def get_dataset(self, db: AsyncSession, dataset_id: str) -> Optional[DatasetModel]:
        """
        Fetch a dataset metadata record from the database.
        """
        result = await db.execute(select(DatasetModel).where(DatasetModel.id == dataset_id))
        return result.scalars().first()

    async def update_dataset_goal(self, db: AsyncSession, dataset_id: str, goal: str) -> Optional[DatasetModel]:
        """
        Update the analysis goal for a specific dataset.
        """
        db_dataset = await self.get_dataset(db, dataset_id)
        if db_dataset:
            db_dataset.analysis_goal = goal
            db.add(db_dataset)
            await db.commit()
        return db_dataset

    async def delete_dataset(self, db: AsyncSession, dataset_id: str) -> bool:
        """
        Deletes a dataset database entry and cleans up the local filesystem spreadsheet.
        """
        db_dataset = await self.get_dataset(db, dataset_id)
        if not db_dataset:
            return False

        # Remove file from local disk storage
        if os.path.exists(db_dataset.file_path):
            os.remove(db_dataset.file_path)

        # Remove database entry
        await db.delete(db_dataset)
        await db.commit()
        return True

dataset_service = DatasetService()
