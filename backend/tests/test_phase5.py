import os
import pytest
import pandas as pd
from unittest.mock import MagicMock
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.chat_models import FakeListChatModel

from services.microsoft.semantic_entities.analysis_goal import AnalysisGoalEntity
from services.microsoft.semantic_entities.dataset_entity import DatasetEntity, ColumnEntity
from services.microsoft.semantic_entities.quality_issue import QualityIssueEntity
from services.microsoft.semantic_entities.recommendation import RecommendationEntity
from services.microsoft.semantic_entities.agent_memory import AgentMemoryEntity
from services.microsoft.semantic_entities.relationship import SemanticRelationship
from services.microsoft.evaluation.evaluator import evaluator_service, LocalEvaluator
from services.microsoft.orchestration.local_runtime import local_runtime_service
from agents.planner.planner_agent import PlannerAgent
from agents.quality.quality_agent import QualityAgent
from agents.evaluation.agent import EvaluationAgent
from agents.graph import build_agent_graph

def test_semantic_entities_validation():
    # 1. Column and Dataset Entity validation
    col = ColumnEntity(
        name="Revenue",
        inferred_type="float",
        null_count=10,
        null_percentage=0.10,
        unique_values=100,
        sample_values=[100.5, 200.0]
    )
    dataset = DatasetEntity(
        entity_id="dataset_123",
        entity_type="Dataset",
        created_by_agent="PlannerAgent",
        filename="sales.csv",
        file_path="/path/to/sales.csv",
        file_size_bytes=1024,
        row_count=1000,
        column_count=1,
        detected_type="csv",
        columns=[col]
    )
    assert dataset.entity_id == "dataset_123"
    assert dataset.columns[0].name == "Revenue"

    # 2. QualityIssueEntity and RecommendationEntity validation
    issue = QualityIssueEntity(
        entity_id="issue_1",
        entity_type="QualityIssue",
        created_by_agent="QualityAgent",
        confidence=0.95,
        dependencies=["col_Revenue"],
        title="Missing Values",
        description="Missing values in Revenue",
        severity="Warning",
        affected_columns=["Revenue"],
        evidence="null_count=10",
        business_impact="Distorts stats"
    )
    rec = RecommendationEntity(
        entity_id="rec_1",
        entity_type="Recommendation",
        created_by_agent="QualityAgent",
        confidence=0.95,
        dependencies=["issue_1"],
        recommendation_text="Impute missing values",
        actionable_steps=["Check source", "Apply median imputation"]
    )
    assert issue.severity == "Warning"
    assert rec.recommendation_text == "Impute missing values"

def test_semantic_relationships():
    rel = SemanticRelationship(
        relationship_id="rel_1",
        source_id="QualityAgent",
        target_id="issue_1",
        relationship_type="creates"
    )
    assert rel.relationship_type == "creates"
    assert rel.source_id == "QualityAgent"

def test_local_evaluator_metrics():
    # Construct a simulated final AgentState
    simulated_state = {
        "dataset_metadata": {
            "column_count": 3
        },
        "quality_result": {
            "findings": [
                {"id": "quality_missing_value_Revenue", "severity": "Critical"},
                {"id": "quality_duplicate_rows", "severity": "Warning"}
            ],
            "recommendations": ["Rec1", "Rec2"]
        },
        "profile_summary": {
            "columns_with_missing_values": 1
        },
        "agent_execution_log": [
            {"type": "agent_step", "status": "completed"},
            {"type": "tool_step", "status": "completed"}
        ]
    }
    
    evaluator = LocalEvaluator()
    result = evaluator.evaluate_state(simulated_state)
    
    assert result.evidence_completeness == 1.0
    assert result.determinism == 1.0
    assert result.recommendation_coverage == 1.0  # 2 recs for 2 findings
    assert result.agent_agreement == 1.0  # profile matches missing values expectation
    assert result.trace_completeness == 1.0
    assert result.overall_analysis_score == 1.0

@pytest.mark.anyio
async def test_full_graph_execution(tmp_path):
    # Create a small dummy CSV file
    csv_file = tmp_path / "sales.csv"
    df = pd.DataFrame({
        "Revenue": [100.5, None, 150.0],
        "ID": [1, 2, 3]
    })
    df.to_csv(csv_file, index=False)

    # Fake LLM that returns pre-determined plan
    llm = FakeListChatModel(responses=["Planner Completed"])

    # Instantiate graph
    graph = build_agent_graph(llm)

    # Initial state
    initial_state = {
        "dataset_path": str(csv_file),
        "goal": "Data Quality Audit",
        "schema_info": [
            {"name": "Revenue", "inferred_type": "float", "null_count": 1, "null_percentage": 0.33, "unique_values": 2},
            {"name": "ID", "inferred_type": "integer", "null_count": 0, "null_percentage": 0.0, "unique_values": 3}
        ],
        "dataset_id": "test_dataset_id",
        "dataset_metadata": {
            "filename": "sales.csv",
            "file_size_bytes": 100,
            "row_count": 3,
            "column_count": 2,
            "detected_type": "csv"
        },
        "dataset_schema": [
            {"name": "Revenue", "type": "float"},
            {"name": "ID", "type": "integer"}
        ],
        "dataset_preview": {
            "columns": ["Revenue", "ID"],
            "data": [[100.5, 1], [None, 2], [150.0, 3]]
        },
        "profile_summary": {
            "columns_with_missing_values": 1,
            "numeric_columns": 2
        },
        "messages": [],
        "current_agent": "system",
        "errors": []
    }

    final_state = await graph.ainvoke(initial_state)

    # Assert basic execution completes and ends up in final state
    assert final_state["current_agent"] == "evaluation"
    assert final_state["current_step"] == "Evaluation Complete"

    # Assert semantic blackboard properties populated
    assert "semantic_goal" in final_state
    assert "semantic_dataset" in final_state
    assert "semantic_issues" in final_state
    assert "semantic_recommendations" in final_state
    assert "semantic_relationships" in final_state
    assert "evaluation_result" in final_state

    # Blackboard meta-versioning verification
    assert final_state["blackboard_version"] == 4
    assert final_state["blackboard_entity_count"] > 5
    assert final_state["blackboard_last_updated_by"] == "EvaluationAgent"
    assert final_state["blackboard_last_trace_id"] != ""


    # Check that relationships contain target structures
    rels = final_state["semantic_relationships"]
    relationship_types = [r["relationship_type"] for r in rels]
    assert "creates" in relationship_types
    assert "contains" in relationship_types
    assert "has" in relationship_types
    assert "generates" in relationship_types

    # Verify tracking registry of local_runtime
    assert len(local_runtime_service.registered_agents) >= 4
    assert len(local_runtime_service.memory_snapshots) >= 4


def test_analyze_endpoint_semantic_response(tmp_path):
    from fastapi.testclient import TestClient
    from main import app
    from unittest.mock import patch, AsyncMock
    
    # Create dummy file to bypass path check
    dummy_csv = tmp_path / "endpoint_data.csv"
    pd.DataFrame({"Revenue": [10.0, None], "ID": [1, 2]}).to_csv(dummy_csv, index=False)
    
    mock_db_dataset = MagicMock()
    mock_db_dataset.id = "test_dataset_uuid"
    mock_db_dataset.file_path = str(dummy_csv)
    mock_db_dataset.filename = "endpoint_data.csv"
    mock_db_dataset.file_size = 200
    mock_db_dataset.row_count = 2
    mock_db_dataset.column_count = 2
    mock_db_dataset.detected_type = "csv"
    mock_db_dataset.schema_info = [
        {"name": "Revenue", "inferred_type": "float", "null_count": 1, "null_percentage": 0.5, "unique_values": 1},
        {"name": "ID", "inferred_type": "integer", "null_count": 0, "null_percentage": 0.0, "unique_values": 2}
    ]
    mock_db_dataset.preview_data = {
        "columns": ["Revenue", "ID"],
        "data": [[10.0, 1], [None, 2]]
    }
    mock_db_dataset.profile_summary = {
        "columns_with_missing_values": 1,
        "numeric_columns": 2
    }
    
    with patch("services.datasets.service.dataset_service.get_dataset", return_value=mock_db_dataset), \
         patch("services.datasets.service.dataset_service.update_dataset_goal", return_value=None):
         
         client = TestClient(app)
         response = client.post(
             "/api/v1/agents/analyze",
             json={"dataset_id": "test_dataset_uuid", "goal": "Data Quality Audit"}
         )
         
         assert response.status_code == 200
         res_data = response.json()
         
         # Check Phase 5 blackboard variables are successfully exposed in the API payload
         assert "semantic_goal" in res_data
         assert res_data["semantic_goal"]["goal_text"] == "Data Quality Audit"
         assert "semantic_dataset" in res_data
         assert "semantic_issues" in res_data
         assert "semantic_recommendations" in res_data
         assert "semantic_relationships" in res_data
         assert "evaluation_result" in res_data
         assert res_data["blackboard_version"] == 4
         assert res_data["blackboard_entity_count"] > 0
         assert res_data["blackboard_last_updated_by"] == "EvaluationAgent"
