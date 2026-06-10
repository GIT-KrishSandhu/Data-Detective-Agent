import pytest
import pandas as pd
from tools.statistics.numeric_summary_tool import run_numeric_summary_tool
from tools.statistics.distribution_analysis_tool import run_distribution_analysis_tool
from tools.statistics.outlier_summary_tool import run_outlier_summary_tool
from tools.statistics.categorical_summary_tool import run_categorical_summary_tool
from tools.statistics.datetime_summary_tool import run_datetime_summary_tool
from tools.statistics.metric_relationship_tool import run_metric_relationship_tool
from tools.statistics.schema_relationship_tool import run_schema_relationship_tool
from services.microsoft.evaluation.powerbi_readiness_engine import readiness_engine
from agents.bi_readiness.bi_readiness_agent import BIReadinessAgent
from langchain_community.chat_models import FakeListChatModel


def test_descriptive_tools():
    # Setup dummy dataframe
    df = pd.DataFrame({
        "Sales": [100.0, 150.0, 200.0, 250.0, 1000.0, 100.0],  # Duplicate value present
        "Product": ["A", "B", "A", "B", "A", "B"],
        "Date": pd.date_range(start="2026-01-01", periods=6, freq="D"),
        "ID": [1, 2, 3, 4, 5, 6]
    })
    
    num_res = run_numeric_summary_tool(df)
    assert "numeric_columns" in num_res
    assert "Sales" in num_res["numeric_columns"]
    assert num_res["numeric_columns"]["Sales"]["mean"] == 300.0


    dist_res = run_distribution_analysis_tool(df)
    assert "distributions" in dist_res
    assert "Sales" in dist_res["distributions"]

    outlier_res = run_outlier_summary_tool(df)
    assert "outliers" in outlier_res
    assert "Sales" in outlier_res["outliers"]

    cat_res = run_categorical_summary_tool(df)
    assert "categorical_columns" in cat_res
    assert "Product" in cat_res["categorical_columns"]

    dt_res = run_datetime_summary_tool(df)
    assert "datetime_columns" in dt_res
    assert "Date" in dt_res["datetime_columns"]

    metric_res = run_metric_relationship_tool(df)
    assert "measures" in metric_res
    assert "Sales" in metric_res["measures"]

    schema_res = run_schema_relationship_tool(df)
    assert "primary_keys" in schema_res
    assert "ID" in schema_res["primary_keys"]

def test_readiness_engine():
    schema_info = [
        {"name": "Sales", "inferred_type": "float", "null_count": 0, "null_percentage": 0.0, "unique_values": 5},
        {"name": "Product", "inferred_type": "string", "null_count": 0, "null_percentage": 0.0, "unique_values": 2},
        {"name": "ID", "inferred_type": "integer", "null_count": 0, "null_percentage": 0.0, "unique_values": 5}
    ]
    quality_findings = [
        {"id": "quality_missing_value_Sales", "title": "Missing Value", "severity": "Warning", "affected_columns": ["Sales"]}
    ]
    metric_pairings = {"measures": ["Sales"], "dimensions": ["Product"]}
    schema_relations = {"primary_keys": ["ID"], "foreign_keys": [], "dim_candidates": [{"table_name": "Product"}], "fact_candidates": [{"table_name": "Sales"}]}
    datetime_summary = {"datetime_columns": {"Date": {"continuity_ratio": 1.0}}}

    res = readiness_engine.evaluate(
        schema_info=schema_info,
        quality_findings=quality_findings,
        metric_pairings=metric_pairings,
        schema_relations=schema_relations,
        datetime_summary=datetime_summary
    )

    assert "readiness_score" in res
    assert 0 <= res["readiness_score"] <= 100
    assert "overall_rating_text" in res
    assert "category_ratings" in res

@pytest.mark.anyio
async def test_bi_readiness_agent(tmp_path):
    csv_file = tmp_path / "test_data.csv"
    df = pd.DataFrame({
        "Sales": [10.0, 20.0, 10.0],
        "ID": [1, 2, 3]
    })
    df.to_csv(csv_file, index=False)

    llm = FakeListChatModel(responses=["BI Readiness mock completed"])
    agent = BIReadinessAgent(name="BIReadinessAgent", llm=llm)

    state = {
        "dataset_path": str(csv_file),
        "goal": "Power BI Preparation",
        "schema_info": [
            {"name": "Sales", "inferred_type": "float", "null_count": 0, "null_percentage": 0.0, "unique_values": 2},
            {"name": "ID", "inferred_type": "integer", "null_count": 0, "null_percentage": 0.0, "unique_values": 3}
        ],

        "dataset_id": "test_dataset_uuid",
        "dataset_metadata": {
            "filename": "test_data.csv",
            "file_size_bytes": 100,
            "row_count": 3,
            "column_count": 2,
            "detected_type": "csv"
        },
        "profile_summary": {
            "numeric_columns": 2,
            "columns_with_missing_values": 0
        },
        "quality_findings": [],
        "agent_execution_log": [],
        "semantic_relationships": [],
        "semantic_memories": [],
        "errors": []
    }

    res = await agent.execute(state)

    assert "bi_readiness_result" in res
    assert "semantic_statistics" in res
    assert "semantic_powerbi_readiness" in res
    assert "semantic_business_metrics" in res
    assert "semantic_distributions" in res
    assert "semantic_aggregation_recommendations" in res
    assert res["bi_evidence_confidence"] == 1.0
    assert res["bi_reasoning_confidence"] == 1.0
