# System Workflow Pipeline

This document details the execution sequence of the Data Detective Agent workflow.

## Phase 1: Intake and Planning
1. **User Action**: User uploads dataset (CSV/XLSX) and submits analysis request specifying the target Goal.
2. **System Node**: `PlannerAgent` executes.
   - Evaluates the Goal.
   - Generates a customized execution plan specifying focal points (e.g., focus on missing values or outliers).
   - Writes the plan back to the global `AgentState`.

## Phase 2: Auditing and Profiling
1. **System Node**: `QualityAgent` scans the dataset path.
   - Collects missing column counts, schemas, and duplicate rows.
   - Appends findings to `quality_report`.
2. **System Node**: `StatisticsAgent` executes descriptive profiles.
   - Generates mean, median, min, max, std dev for numerical columns.
   - Appends statistics to `statistical_summary`.
3. **System Node**: `VisualizationAgent` creates chart definitions.
   - Writes Plotly-compatible JSON specifications representing distributions and correlations.
   - Links each chart schema to a data query for traceability.

## Phase 3: Cleaning Policy Recommendation
1. **System Node**: `CleaningAgent` executes.
   - Reviews findings from the `QualityAgent`.
   - Formulates a list of proposed cleaning operations (e.g., fill null values, drop rows).
   - Appends list to `suggested_cleaning_actions` in the state.
2. **Human-in-the-Loop Gateway**:
   - The graph pauses or returns control to the backend application.
   - The client application fetches suggested cleaning actions and renders them with code previews.
   - The user selects which actions to approve.
   - Approved list is saved to `user_approved_cleaning_actions`, and `cleaning_applied` is set to `True`.

## Phase 4: Verification and Reporting
1. **System Node**: `CriticAgent` executes.
   - Verifies that no forecasting steps exist.
   - Cross-checks statements for hallucinations.
2. **System Node**: `EvaluationAgent` executes.
   - Validates metrics counts.
   - Logs query verification checks.
3. **System Node**: `ReportAgent` executes.
   - Combines findings and plans into a final markdown-formatted report.
   - Saves final report to `final_report`.
4. **Final Output**: System displays final report and provides download links for cleaned datasets and interactive visualizations.
