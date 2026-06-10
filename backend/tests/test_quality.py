import os
import pytest
import pandas as pd
from unittest.mock import MagicMock

from tools.quality.missing_value_tool import run_missing_value_tool
from tools.quality.duplicate_detector import run_duplicate_detector
from tools.quality.constant_column_detector import run_constant_column_detector
from tools.quality.mixed_type_detector import run_mixed_type_detector
from tools.quality.identifier_detector import run_identifier_detector
from tools.quality.high_cardinality_detector import run_high_cardinality_detector

from agents.base.agent_result import AgentResult
from agents.quality.finding import QualityFinding
from agents.quality.quality_agent import QualityAgent

def test_missing_value_tool():
    df = pd.DataFrame({
        "col1": [1, None, 3],
        "col2": [None, None, "foo"]
    })
    res = run_missing_value_tool(df)
    assert res["total_missing"] == 3
    assert res["columns"]["col1"]["null_count"] == 1
    assert res["columns"]["col2"]["null_count"] == 2
    assert res["columns"]["col2"]["null_percentage"] == pytest.approx(2/3)

def test_duplicate_detector():
    df = pd.DataFrame({
        "col1": [1, 2, 1],
        "col2": ["foo", "bar", "foo"]
    })
    res = run_duplicate_detector(df)
    assert res["duplicate_rows_count"] == 1
    assert res["duplicate_percentage"] == pytest.approx(1/3)

def test_constant_column_detector():
    df = pd.DataFrame({
        "col1": [1, 1, 1],
        "col2": ["foo", "bar", "baz"]
    })
    res = run_constant_column_detector(df)
    assert len(res["constant_columns"]) == 1
    assert res["constant_columns"][0]["column"] == "col1"
    assert res["constant_columns"][0]["value"] == 1

def test_mixed_type_detector():
    df = pd.DataFrame({
        "col1": [1, "foo", 3],
        "col2": ["foo", "bar", "baz"]
    })
    res = run_mixed_type_detector(df)
    assert "col1" in res["mixed_type_columns"]
    assert "col2" not in res["mixed_type_columns"]
    assert "str" in res["mixed_type_columns"]["col1"]["types_found"]
    assert "int" in res["mixed_type_columns"]["col1"]["types_found"]

def test_identifier_detector():
    df = pd.DataFrame({
        "id_col": [1, 2, 3],
        "val_col": ["foo", "foo", "bar"]
    })
    res = run_identifier_detector(df)
    assert len(res["identifier_columns"]) == 1
    assert res["identifier_columns"][0]["column"] == "id_col"
    assert "ID keyword" in res["identifier_columns"][0]["reason"]

def test_high_cardinality_detector():
    df = pd.DataFrame({
        "cat_col": [f"val_{i}" for i in range(100)],
        "val_col": [1] * 100
    })
    res = run_high_cardinality_detector(df)
    assert len(res["high_cardinality_columns"]) == 1
    assert res["high_cardinality_columns"][0]["column"] == "cat_col"
    assert res["high_cardinality_columns"][0]["unique_count"] == 100

def test_agent_result_contract():
    res = AgentResult(
        agent_name="TestAgent",
        summary="A summary",
        reasoning="Some reasoning",
        confidence=0.9,
        findings=[],
        recommendations=["Rec1"],
        tool_trace=[{"tool_name": "t1", "execution_time_ms": 10}],
        execution_time_ms=50
    )
    assert res.agent_name == "TestAgent"
    assert res.execution_time_ms == 50

@pytest.mark.anyio
async def test_quality_agent_execution(tmp_path):
    # Create a dummy CSV file to load
    csv_file = tmp_path / "test_data.csv"
    df = pd.DataFrame({
        "Revenue": [10.5, None, 15.0],
        "ID_field": [1, 2, 3],
        "Constant": [5, 5, 5]
    })
    df.to_csv(csv_file, index=False)

    # Instantiate QualityAgent with a fake LLM
    llm = MagicMock()
    agent = QualityAgent(name="QualityAgent", llm=llm)

    state = {
        "dataset_path": str(csv_file),
        "goal": "Data Quality Audit",
        "dataset_metadata": {"filename": "test_data.csv"},
        "agent_execution_log": []
    }

    updates = await agent.execute(state)

    # Verify state updates
    assert "quality_result" in updates
    assert "quality_findings" in updates
    assert "quality_recommendations" in updates
    assert "agent_execution_log" in updates

    q_res = updates["quality_result"]
    assert q_res["agent_name"] == "QualityAgent"
    assert len(q_res["findings"]) > 0

    # Validate execution step events logged
    log = updates["agent_execution_log"]
    events = [l.get("event") for l in log if l.get("type") == "telemetry_event"]
    assert "quality_started" in events
    assert "quality_completed" in events
    assert "blackboard_updated" in events

    # Validate tool steps ran and are logged
    tool_steps = [l for l in log if l.get("type") == "tool_step"]
    assert len(tool_steps) == 6
    tool_names = [t["tool_name"] for t in tool_steps]
    assert "Missing Value Tool" in tool_names
    assert "Duplicate Detector" in tool_names
