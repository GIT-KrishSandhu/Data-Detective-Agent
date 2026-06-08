import pytest
import pandas as pd
from unittest.mock import MagicMock

from tools.profile_summary import calculate_profile_summary
from agents.planner.planner_agent import PlannerAgent, GOAL_WORKFLOWS

def test_profile_summary_generation():
    """
    Test deterministic profile summary generation using a mock pandas DataFrame.
    """
    data = {
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", None],  # Contains 1 missing value, object/string type
        "revenue": [10.5, 20.0, 15.0],   # Numeric float type
        "is_active": [True, False, True], # Boolean type
        "signup_date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]) # Datetime type
    }
    df = pd.DataFrame(data)
    
    summary = calculate_profile_summary(df)
    
    assert summary["numeric_columns"] == 2      # id is integer, revenue is float -> 2
    assert summary["categorical_columns"] == 1  # name is string
    assert summary["boolean_columns"] == 1      # is_active is boolean
    assert summary["datetime_columns"] == 1     # signup_date is datetime
    assert summary["columns_with_missing_values"] == 1  # name has a None/null value

def test_planner_workflow_generation_all_goals():
    """
    Test workflow steps mapping and reasoning for each goal type.
    """
    mock_llm = MagicMock()
    planner = PlannerAgent(name="TestPlanner", llm=mock_llm)
    
    metadata = {"filename": "test.csv", "row_count": 100}
    profile_summary = {
        "numeric_columns": 3,
        "categorical_columns": 2,
        "datetime_columns": 1,
        "boolean_columns": 1,
        "columns_with_missing_values": 2
    }

    # Test all 4 goals
    goals = [
        "Data Quality Audit",
        "Exploratory Data Analysis",
        "Executive Summary",
        "Power BI Preparation"
    ]

    for goal in goals:
        plan = planner.plan_workflow(goal, metadata, profile_summary)
        
        assert plan["goal"] == goal
        assert len(plan["workflow_steps"]) == 5
        assert plan["workflow_steps"] == GOAL_WORKFLOWS[goal]
        assert plan["confidence"] > 0.0
        assert plan["confidence"] <= 1.0
        assert len(plan["reasoning"]) > 0
        assert "null" in plan["reasoning"] or "missing" in plan["reasoning"]

def test_planner_workflow_fuzzy_matching():
    """
    Test goal name fuzzy mapping to default goal keys.
    """
    mock_llm = MagicMock()
    planner = PlannerAgent(name="TestPlanner", llm=mock_llm)
    
    profile_summary = {
        "numeric_columns": 1,
        "categorical_columns": 1,
        "datetime_columns": 0,
        "boolean_columns": 0,
        "columns_with_missing_values": 0
    }

    # "eda" should fuzzy map to "Exploratory Data Analysis"
    plan = planner.plan_workflow("run some eda", {}, profile_summary)
    assert plan["goal"] == "Exploratory Data Analysis"
    
    # "power bi" should map to "Power BI Preparation"
    plan = planner.plan_workflow("prepare columns for power bi report", {}, profile_summary)
    assert plan["goal"] == "Power BI Preparation"
