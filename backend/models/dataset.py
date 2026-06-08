import uuid
from datetime import datetime, timezone
# pyrefly: ignore [missing-import]
from sqlalchemy import String, Integer, DateTime, JSON
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column

from database.session import Base

class DatasetModel(Base):
    """
    SQLAlchemy Database Model for Datasets.
    Persists dataset metadata, column schema definitions, visual preview JSONs,
    and profile summary indicators for goal-driven workflow planning.
    """
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    detected_type: Mapped[str] = mapped_column(String(50), nullable=False)  # csv or xlsx
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    column_count: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Ingestion upgrades for Phase 3
    analysis_goal: Mapped[str] = mapped_column(String(100), nullable=True)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    profile_summary: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Store schema as a list/dict JSON block containing column descriptions
    schema_info: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Store dynamic preview showing top 20 rows of headers + records
    preview_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
