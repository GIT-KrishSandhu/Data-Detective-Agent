# Agent League - Responsibilities Matrix

The platform is designed around 8 specialized agents. Below is the detailed breakdown of their individual responsibilities and architectural constraints.

---

### 1. Planner Agent (`PlannerAgent`)
* **Objective**: Define the analysis pathway based on user goal and initial dataset schema.
* **Responsibilities**:
  - Parse the selected goal (`quality`, `eda`, `summary`, `powerbi`).
  - Read sample schema information.
  - Generate a step-by-step custom planning dictionary.
* **Constraints**:
  - Cannot specify tasks outside the capability of the agent league (e.g. no database creation, no external API fetching).

---

### 2. Quality Agent (`QualityAgent`)
* **Objective**: Inspect the dataset for anomalies and integrity failures.
* **Responsibilities**:
  - Identify missing values, null densities, and duplicate rows.
  - Scan for schema mismatches (e.g. string values inside numeric fields).
  - Flags potential structural gaps (e.g. missing primary keys).
* **Constraints**:
  - Must report only structural and type issues; must not attempt to alter the data.

---

### 3. Statistics Agent (`StatisticsAgent`)
* **Objective**: Perform mathematical profile analysis on the data.
* **Responsibilities**:
  - Calculate descriptive statistics (mean, median, standard deviation, quartiles).
  - Compute column correlations.
  - Detect mathematical outliers.
* **Constraints**:
  - **Strict Principle**: Banned from generating forecasting models, predictive trends, or time-series projections.

---

### 4. Visualization Agent (`VisualizationAgent`)
* **Objective**: Generate clean and interactive visual representations.
* **Responsibilities**:
  - Design Plotly chart JSON specifications (histograms, scatter plots, correlation heatmaps).
  - Link each chart to the SQL statement or Pandas statement that generated the data.
* **Constraints**:
  - Charts must have trace validation (no mock coordinates or hallucinated points).

---

### 5. Cleaning Agent (`CleaningAgent`)
* **Objective**: Suggest resolutions for anomalous rows and columns.
* **Responsibilities**:
  - Scan Quality Agent alerts and design resolutions (e.g., column drop, median imputation, type casting).
  - Generate clear python script previews for human verification.
* **Constraints**:
  - Cannot execute modifications without user confirmation.

---

### 6. Critic Agent (`CriticAgent`)
* **Objective**: Serve as the safety guardrail for the agent network.
* **Responsibilities**:
  - Inspect plans and generated insights for forecasting attempts.
  - Scan reports for unsupported statements or hallucinated observations.
  - Enforce compliance with the system's core principles.
* **Constraints**:
  - Has the authority to flag violations and request re-execution of previous nodes.

---

### 7. Evaluation Agent (`EvaluationAgent`)
* **Objective**: Verify mathematical and evidence integrity.
* **Responsibilities**:
  - Re-run SQL queries to verify that statistics match final counts.
  - Verify that summary claims in reports map exactly to structured metrics.
* **Constraints**:
  - Must write verification reports to state, highlighting any discrepancies.

---

### 8. Report Agent (`ReportAgent`)
* **Objective**: Synthesize findings into the final report.
* **Responsibilities**:
  - Compile markdown-formatted summaries of the analysis.
  - Embed chart configurations and data quality logs.
  - List human-approved changes for complete traceability.
* **Constraints**:
  - Cannot include insights that were not validated by the Evaluation and Critic Agents.
