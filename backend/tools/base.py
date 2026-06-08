"""
Abstract tool interfaces for the Data Detective Agent framework.
These define the operations available to specialized agents for inspecting,
profiling, and editing spreadsheets, maintaining structural and trace verification.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

class DatasetInspectorInput(BaseModel):
    dataset_path: str = Field(description="Absolute path to the dataset spreadsheet (CSV or XLSX).")
    num_rows: int = Field(default=5, description="Number of sample rows to fetch.")

class DatasetInspectorTool(BaseTool, ABC):
    name: str = "dataset_inspector"
    description: str = "Inspect columns, data types, sample values, and file metadata."
    args_schema: type[BaseModel] = DatasetInspectorInput

    @abstractmethod
    def _run(self, dataset_path: str, num_rows: int = 5) -> Dict[str, Any]:
        """Synchronous execution implementation."""
        pass


class StatisticalProfilerInput(BaseModel):
    dataset_path: str = Field(description="Absolute path to the dataset spreadsheet.")
    columns: Optional[List[str]] = Field(default=None, description="Select list of numeric columns to profile.")

class StatisticalProfilerTool(BaseTool, ABC):
    name: str = "statistical_profiler"
    description: str = "Calculate summary statistics (mean, median, min, max, std dev) for columns."
    args_schema: type[BaseModel] = StatisticalProfilerInput

    @abstractmethod
    def _run(self, dataset_path: str, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        pass


class CleaningExecutorInput(BaseModel):
    dataset_path: str = Field(description="Absolute path to the dataset spreadsheet.")
    action_id: str = Field(description="The unique identifier of the approved cleaning action.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Custom parameters to configure the cleaning action.")

class CleaningExecutorTool(BaseTool, ABC):
    name: str = "cleaning_executor"
    description: str = "Apply specific, human-approved cleaning operations to the dataset."
    args_schema: type[BaseModel] = CleaningExecutorInput

    @abstractmethod
    def _run(self, dataset_path: str, action_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes a cleaning action.
        CRITICAL: Requires confirmation of prior human approval before execution.
        """
        pass
