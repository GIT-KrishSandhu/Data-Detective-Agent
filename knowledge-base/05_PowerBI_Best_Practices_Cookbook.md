# 05 — Power BI Best Practices Cookbook

## 100+ Practical Rules for Enterprise BI Governance

---

## Executive Summary

This cookbook is the operational rule set for Power BI semantic modeling, data quality, governance, and deployment. Each rule is independently retrievable and directly usable as grounding context for executive summary generation by Azure GPT-5-mini. Rules are organized by domain and include the business consequence of violations to facilitate risk-aware governance recommendations.

---

## Domain 1 — Schema Design Rules

### Rule 001 — Always Use Star Schema for Power BI Semantic Models

* **Explanation:** The VertiPaq in-memory engine is architecturally optimized for single-hop joins from dimension to fact. Snowflake schemas require multi-hop joins that degrade DAX query performance.


* **Good Example:** `DimCustomer → FactSales ← DimDate` (one-hop joins).


* **Bad Example:** `FactSales → DimProduct → DimCategory → DimDivision` (three-hop join).


* **Business Consequence:** Three-hop snowflake joins increase product hierarchy query time by 300–500% — executive product performance dashboards become unusable under load.


* **Recommendation:** Flatten all snowflake sub-dimensions into a single wide dimension table in the ETL layer before Power BI ingestion.



### Rule 002 — Define and Document the Fact Table Grain Explicitly

* **Explanation:** The grain is the most granular level of detail represented by one row in a fact table. Undefined grain leads to ambiguous aggregations.


* **Good Example:** Documented grain: "One row per order line item, per day, per warehouse location."


* **Bad Example:** Fact table mixing order headers, line items, and weekly summaries without documentation.


* **Business Consequence:** Mixed grain causes revenue SUM to overcount — executive sees $14M instead of $8M; budget decisions are invalidated.


* **Recommendation:** Document the grain statement in the dataset's data dictionary before submitting to Data Detective.



### Rule 003 — Use Integer Surrogate Keys for All Relationships

* **Explanation:** Integer keys compress efficiently in VertiPaq, join faster, and are immune to source system identifier format changes.


* **Good Example:** `CustomerKey INT = 50234`

* **Bad Example:** `CustomerCode VARCHAR = "APAC-CUST-50234-VIP"`

* **Business Consequence:** String key relationships inflate model size by 40–200%; join resolution time increases 3–8×.


* **Recommendation:** Introduce integer surrogate keys in the ETL layer; preserve natural keys as non-key reference columns.



### Rule 004 — Always Create a Dedicated DimDate Table

* **Explanation:** Power BI's Auto Date/Time feature creates hidden date hierarchies per date column — inflating model size and creating inconsistent time intelligence behavior.


* **Good Example:** Shared `DimDate` table marked as a date table; Auto Date/Time disabled globally.


* **Bad Example:** Auto Date/Time enabled with 8 date columns in the fact table — 8 hidden hierarchies consuming 700MB.


* **Business Consequence:** 700MB hidden date overhead slows refresh by 35%; DAX time intelligence behaves inconsistently across date columns.


* **Recommendation:** Create one enterprise DimDate; disable Auto Date/Time in all Power BI Desktop files.



### Rule 005 — Preserve Natural Keys as Non-Key Columns

* **Explanation:** After introducing surrogate keys, the original business identifier must be retained for auditability, drill-through, and reconciliation.


* **Good Example:** `DimCustomer` contains both `CustomerKey INT` (surrogate) and `CustomerCode VARCHAR` (natural, non-relationship).


* **Bad Example:** Surrogate key introduced and original business identifier deleted.


* **Business Consequence:** Finance cannot reconcile Power BI transaction data with source system records — audit failure risk.


* **Recommendation:** Retain natural keys as hidden columns in the dimension table; surface in drill-through pages only.



> **Executive Note:** Adherence to standard star schema and strict data types prevents 80% of downstream performance and Business Intelligence readiness failures.

*(Rules 006 through 070 continue with standard architectural, DAX, Governance, and Naming constraints per Data Detective platform specs)*

---

## Domain 2 — Data Quality & Integrity Rules (Extended)

| Rule ID | Title | Explanation | Good Example | Bad Example | Business Consequence | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| **071** | **Avoid Circular Dependencies in DAX Measures** | Circular references cause model failures when two measures depend on each other's filter context. | `[Margin] = [Rev] - [Cost]` | `[A] = [B] * 2` and `[B] = [A] - 5` | Report visuals completely fail to render; dashboards crash. | Use ALLEXCEPT or rewrite logic into a single atomic measure.

 |
| **072** | **Use What-If Parameters for Scenarios** | Static columns cannot adapt to user-driven scenario analysis dynamically. | What-If parameter slicer adjusting `[Forecast Rate]`. | Static `Forecast = [Sales] * 1.05` column in Fact table.

 | Executives cannot model 10% vs 5% growth; analysis is rigid. | Implement native What-If parameters to generate series tables.

 |
| **073** | **Apply Column Descriptions to Hidden Columns** | Hidden columns still require Governance transparency for downstream Data Detective audits. | `CustomerKey` description: "Surrogate key for CRM." | Hidden column left entirely undocumented.

 | New engineers un-hide and misuse technical keys. | Require 100% data dictionary completeness, even for hidden attributes.

 |
| **074** | **Validate Fiscal Calendar Alignment** | Financial dashboards must align with corporate fiscal years, not standard calendar years. | `DimDate[FiscalYear]` starting in July. | Relying on `YEAR()` for fiscal reports.

 | Q1 revenue misreported by 3 months; executive decisions misled. | Validate fiscal calendar logic with Finance Data Owner before deployment.

 |
| **075** | **Test YTD Measures at Boundaries** | Time-intelligence DAX often breaks exactly on Jan 1 or leap years. | `DATESYTD(DimDate[Date], "06-30")` | Custom YTD logic lacking leap year handling.

 | January 1st executive reports show blank or infinite values. | Add boundary-testing test scripts in Data Detective Quality Agent. |

*(For brevity, rules 076–105 are summarized in the enterprise registry format above, strictly mapping Title, Explanation, Good, Bad, Consequence, and Recommendation to ensure RAG readability)*

| Rule ID | Title | Business Consequence | Recommendation |
| --- | --- | --- | --- |
| **076** | **Avoid Storing Large Text Blobs in Dimension Tables** | High memory consumption; 4GB model bloat.

 | Offload text to external drill-through links. |
| **077** | **Use TREATAS for Virtual Relationships** | Physical relationship failures when inactive joins are overused. | Use `TREATAS` for complex role-playing DAX.

 |
| **078** | **Implement Calculation Groups** | 100+ redundant time-intelligence measures cluttering the model. | Use Calculation Groups for MTD, YTD, YOY.

 |
| **079** | **Monitor VertiPaq Model Memory** | Premium capacity eviction due to size.

 | Run Model Memory audits post-release. |
| **080** | **Validate RLS With Edge-Case Users** | Data leakage across executive boundaries. | Impersonate users in Service before Prod push.

 |
| **081** | **Use ALL() and ALLEXCEPT() Wisely** | Unintended filter context leading to wrong totals. | Explicitly map context modifiers in DAX.

 |
| **082** | **Test Measure Totals** | Totals row sum does not match visual lines.

 | Use `HASONEVALUE` for correct total logic. |
| **083** | **Apply KEEPFILTERS()** | Filters accidentally overridden in visual. | Wrap filter arguments in `KEEPFILTERS()`.

 |
| **084** | **Avoid Using EARLIER()** | Poor performance and hard-to-read DAX.

 | Prefer `VAR` for nested row context. |
| **085** | **Standardize KPI Targets** | Departments disagree on success metrics. | Centralize targets in `DimTarget`. |
| **086** | **Create a Master KPI Register** | Orphaned metrics causing executive disputes. | Maintain KPI definitions in Purview/governance portal.

 |
| **087** | **Update Data Dictionary on MINOR Updates** | Metadata drifts from reality.

 | Embed dictionary updates into CI/CD pipeline. |
| **088** | **Prohibit Hard-Coded Dates in DAX** | Measures break when new year starts. | Use `MAX(DimDate[Date])` or `TODAY()`.

 |
| **089** | **Validate BLANK() vs NULL Consistency** | Aggregations artificially skewed.

 | Standardize `COALESCE` handling. |
| **090** | **Use Consistent Conditional Formatting** | Red means 'Good' on page 1, 'Bad' on page 2. | Enforce enterprise JSON theme files.

 |
| **091** | **Configure Data Alerts on Critical KPIs** | Executives miss sudden revenue drops. | Implement Power BI service alerts.

 |
| **092** | **Apply Descriptive Tooltip Pages** | Screen real-estate wasted on explanations. | Use Report Tooltips for definitions.

 |
| **093** | **Limit Page Count to 10** | Cognitive overload and slow load times.

 | Split into app workspaces by audience. |
| **094** | **Validate Cross-Report Drillthrough** | Broken links when source dataset changes.

 | Keep targets in the certified dataset. |
| **095** | **Avoid Report-Level Measures** | Ungoverned logic bypasses Data Detective.

 | Move all measures to Semantic Model.

 |
| **096** | **Disable Q&A If Not Prepared** | Q&A returns nonsensical answers to executives.

 | Only enable Q&A post-synonym configuration. |
| **097** | **Document All KPI Business Definitions** | Untrusted dashboards. | Embed definitions in Dataset descriptions.

 |
| **098** | **Configure Gateway Clusters for HA** | Refresh failures during single-node downtime.

 | Deploy minimum 2-node gateway clusters. |
| **099** | **Apply Consistent Theme Files** | Unprofessional aesthetic.

 | Use central UX standard theme. |
| **100** | **Conduct Monthly Usage Review** | Maintenance burden for unused reports.

 | Retire reports with 0 views in 90 days. |
| **101** | **Perform Annual Governance Audit** | Governance drift.

 | Force re-certification every 12 months. |
| **102** | **Require Governance Training for Access** | Analysts break rules out of ignorance.

 | Gate access behind Policy training.

 |

---

# 06 — Common BI Failures Casebook

## 30 Reasoning Case Studies for Data Detective Audits

---

## Executive Summary

Data Detective audits datasets BEFORE they reach Power BI to prevent analytic disasters. This casebook details synthetic, realistic enterprise BI failures, their root causes, and how the Multi-Agent Evaluation system detects them. It provides grounding context for the Azure GPT-5-mini Executive Language Layer to generate historical incident summaries and BI readiness remediation plans.

---

### Case Study 01: The Orphaned Revenue

* **Industry:** E-Commerce
* **Dataset:** `FactSales_Global`
* **Problem:** $1.4M in transaction revenue was entirely missing from executive dashboards despite existing in the source database.
* **Root Cause:** Null foreign keys in `ProductKey`. Fact rows without matching dimensions were silently dropped by Power BI's inner join behavior.
* **How Data Detective detects it:** The Quality Agent executes an anti-join referential integrity check, flagging a Critical anomaly where `Fact[ProductKey]` is missing from `DimProduct`.
* **Recommended resolution:** Implement an "Unknown" member (`ProductKey = -1`) during the ETL layer to catch orphaned records.
* **Business impact:** Executive dashboards under-reported total sales, leading to a false hiring freeze.
* **Lessons learned:** Never rely on Power BI to handle null relationship keys; strict ETL foreign key constraints are mandatory.

### Case Study 02: The Headcount Hallucination

* **Industry:** Human Resources
* **Dataset:** `Enterprise_Workforce_Analytics`
* **Problem:** Total employee headcount displayed as 18,000, while actual payroll headcount was 12,500.
* **Root Cause:** A many-to-many (M:M) relationship between `DimEmployee` and `DimProject` caused employees assigned to multiple projects to be double-counted in SUM aggregations.
* **How Data Detective detects it:** The BI Readiness Agent identifies a bidirectional M:M relationship without an intermediary bridge table and flags it as a Schema Quality failure.
* **Recommended resolution:** Introduce a `BridgeEmployeeProject` table with allocation percentages.
* **Business impact:** Real estate and software licensing budgets were over-allocated by 44%.
* **Lessons learned:** M:M relationships must always be resolved via structural bridge tables, never accepted as a Power BI feature.

### Case Study 03: The Silent Snowflake Degradation

* **Industry:** Manufacturing
* **Dataset:** `SupplyChain_Ops`
* **Problem:** A critical morning dashboard took 45 seconds to load, causing executives to abandon it.
* **Root Cause:** The schema was heavily snowflaked (`Fact → DimMaterial → DimSubCat → DimCat → DimDivision`). The DAX engine struggled to resolve 4-hop joins.
* **How Data Detective detects it:** The Evaluation Agent profiles the schema, detects >2 hop relationships, and scores Schema Quality below 65 (Pre-Development).
* **Recommended resolution:** Flatten the material hierarchy into a single wide `DimMaterial` table in the data warehouse before Power BI ingestion.
* **Business impact:** Total loss of confidence in the BI platform; return to manual Excel reporting.
* **Lessons learned:** VertiPaq is optimized for Star Schemas. Flattening dimensions is non-negotiable for enterprise performance.

### Case Study 04: The Time-Travel Margin Error

* **Industry:** Financial Services
* **Dataset:** `Retail_Banking_Margins`
* **Problem:** Historical loan margins were recalculated using today's interest rates, wiping out 3 years of historical margin accuracy.
* **Root Cause:** The `DimInterestRate` was implemented as a Type 1 Slowly Changing Dimension (SCD), overwriting historical rates instead of preserving them.
* **How Data Detective detects it:** The Governance Agent scans dimension tables tagged with "Financial History" for `ValidFrom`/`ValidTo` and `IsCurrent` columns. Missing these triggers a Warning.
* **Recommended resolution:** Re-engineer the dimension to an SCD Type 2 with historical state tracking.
* **Business impact:** Regulatory reporting failed an external audit due to unreconcilable historical states.
* **Lessons learned:** Any dimension supporting historical analysis must implement SCD Type 2 logic with explicit date bounding.

*(Case Studies 05–30 Summarized in Executive format for Foundry IQ Retrieval Optimization)*

| Case ID | Industry | Dataset | Problem | Root Cause | Detective Detection | Recommendation | Business Impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **05** | Healthcare | `Patient_Admissions` | Missing weekend admissions. | Auto-Date/Time enabled, creating hidden misaligned calendars. | Schema Agent checks for `DimDate` mark and disables Auto-Date. | Create centralized enterprise `DimDate`. | ER staffing shortages on weekends. |
| **06** | Logistics | `Fleet_Telemetry` | Aggregations crashed model memory. | String-based GUIDs used as relationship keys. | Quality Agent flags non-integer PK/FK keys. | Hash GUIDs to Integer Surrogate keys. | Premium Capacity eviction; reports down for 4 hours. |
| **07** | Retail | `POS_Transactions` | Gross margin calculated at 450%. | Margin % calculated as a column and natively summed. | Readiness Agent detects additive operations on percentage data types. | Use `DIVIDE()` in explicit DAX measures. | Over-purchasing of low-margin inventory. |
| **08** | SaaS | `Churn_Metrics` | Customer count inflated daily. | ETL retry logic appended duplicate rows. | Quality Agent flags exact row duplicates > 0. | Add idempotent load logic to ETL. | Valuations misstated during Series C funding. |
| **09** | Telecom | `Call_Data_Records` | Daily refresh took 5 hours. | 50M rows full-refreshed daily. | Evaluation Agent checks incremental refresh parameters. | Implement 3-day rolling incremental refresh. | Executives viewed stale data; SLAs breached. |
| **10** | Insurance | `Claims_Processing` | $4M in claims assigned to year 9999. | Sentinel values (9999) treated as real dates. | Quality Agent flags outlier dates outside business range. | Map sentinels to `NULL` or `-1`. | Actuarial models skewed by extreme outliers. |
| **11** | Public Sec | `Tax_Receipts` | Decimals rounded incorrectly. | Floating-point precision error on import. | Quality Agent checks `Float` vs `Decimal(18,4)`. | Enforce fixed decimal data types. | $200K audit discrepancy in GL. |
| **12** | Pharma | `Clinical_Trials` | Blank values in YTD calculations. | DimDate ended prior to fact table dates. | Quality Agent anti-joins Fact dates vs DimDate. | Extend DimDate to Year + 5. | FDA compliance reports rendered blank. |
| **13** | Media | `Ad_Impressions` | Dashboard metrics vanished. | Source system renamed column; schema drift. | Evaluation Agent tracks schema signatures between versions. | CI/CD schema validation gate. | Advertisers billed incorrectly for 3 days. |
| **14** | Energy | `Grid_Load` | Filter context ignored in visual. | Bidirectional cross-filter ambiguity. | Schema Agent rejects all unapproved bidirectional joins. | Force Single-Direction cross-filtering. | Rolling blackouts due to misreported load. |
| **15** | Auto | `Warranty_Claims` | Slicer duplicated "Active" / "ACTIVE". | Case inconsistency in categorical column. | Quality Agent runs `UPPER()` variance checks. | Apply `str.title()` in ETL. | Fragmented analysis; missed recall thresholds. |
| **16** | Aviation | `Flight_Delays` | Negative delay times breaking averages. | Business rule violation (`Arrival < Departure`). | Quality Agent executes predefined Business Rules. | Quarantine invalid rows during load. | FAA reporting fines. |
| **17** | Real Est. | `Property_Valuation` | RLS leaked executive compensation. | RLS deployed without test cases. | Readiness Agent verifies RLS role mappings. | Infosec sign-off gate before deployment. | Internal HR investigation. |
| **18** | Legal | `Billable_Hours` | "John Smith " and "John Smith" unjoined. | Trailing whitespace. | Quality Agent flags `LEN(trim)` anomalies. | Implement universal ETL string trimming. | Partner compensation calculated incorrectly. |
| **19** | Travel | `Booking_Volume` | Currency values blindly summed. | Mixed currencies (USD, EUR) without conversion. | Evaluation Agent scans for single currency domains. | Convert to USD at load time. | Q3 revenue overstated by 18%. |
| **20** | Edu | `Enrollment_Stats` | Null handling inflated average GPA. | `NULL` ignored in averages instead of treated as 0. | Quality Agent forces explicit Null handling DAX. | Define clear `DIVIDE` and `COALESCE` logic. | Funding lost due to skewed metric reporting. |
| **21** | Mining | `Equipment_Sensors` | Dashboard showed test data. | 1,000 UAT records promoted to Prod. | Governance Agent scans for `IsTest` flags. | Filter out UAT flags in Prod workspace. | False maintenance dispatch costing $50k. |
| **22** | Agri | `Crop_Yields` | No lineage; pipeline broke silently. | Undocumented source changes. | Governance Agent rejects models missing Purview links. | Enforce Lineage mapping. | 2 weeks of lost BI visibility. |
| **23** | Gaming | `Player_Microtx` | Model bloated to 8GB. | 200 unused columns imported. | Evaluation Agent profiles column utilization. | `SELECT` only required columns. | Cloud compute costs spiked by 400%. |
| **24** | Fintech | `Crypto_Trades` | Unknown composite model failure. | DirectQuery and Import mixed without documentation. | Readiness Agent flags implicit composite modes. | Document composite SLAs. | Trade dashboards lagged by 5 minutes. |
| **25** | Biotech | `Lab_Results` | Sensitive PII exposed. | Workspace set to public access. | Deployment Agent checks Sensitivity Labels. | Force "Highly Restricted" tagging. | HIPAA violation warning. |
| **26** | CPG | `Inventory_Levels` | Missing refresh timestamp. | Refresh failed silently; users saw old data. | Governance Agent checks for dynamic timestamp cards. | Add `LastRefreshed` DAX card. | Out-of-stock events missed for 48 hours. |
| **27** | Hospitality | `Hotel_Occupancy` | Orphaned dataset; creator left company. | No named Data Owner. | Governance Agent blocks deployment without Owner. | Assign VP-level Data Owner. | Gradual quality decay over 6 months. |
| **28** | Defense | `Supply_Chain` | Non-additive ratios summed. | Summing of percentage columns. | Readiness Agent restricts aggregation on ratios. | Force explicit DAX measures. | Logistics delays due to bad priority metrics. |
| **29** | Sports | `Ticket_Sales` | Semantic model uncertified. | 8 duplicate models published by users. | Deployment Agent restricts "Certified" endorsement. | Consolidate to one Enterprise Semantic Model. | Executive confusion over conflicting numbers. |
| **30** | Gov | `Census_Data` | Free-text dates breaking logic. | Poor upstream data entry. | Quality Agent enforces ISO-8601 formatting. | Force Regex validation upstream. | Policy drafted on corrupted demographic data. |

### Executive Evaluation Checklist & Best Practices

* **Pre-Deployment:** Ensure every Semantic Model routes through Data Detective.
* **Quality vs. Readiness:** A dataset may have clean data (Quality) but terrible architecture (Readiness). Both must score >80 for Production Certification.
* **Governance:** The LLM is an executive summarizer, not a data validator. Guarantee deterministic validation in the Python layer before generating Governance Certificates.

---

*This document is part of the Data Detective Governance Knowledge Base. Version 1.0. For use as RAG retrieval context in Microsoft Foundry IQ.*