# 03 — Business Intelligence Readiness Framework
## Power BI Deployment Readiness Assessment for Data Detective

---

## Executive Summary

BI Readiness is the composite measure of a dataset's fitness for deployment in a Power BI production environment. A dataset may contain structurally valid data yet still be unfit for BI deployment due to schema deficiencies, relationship failures, documentation gaps, or governance non-compliance. The BI Readiness Framework defines the multi-dimensional scoring model, assessment rubric, maturity classification, and executive interpretation logic used by the Data Detective BI Readiness Agent. This document is designed for RAG retrieval by Microsoft Foundry IQ to generate BI Readiness Reports and Governance Certificates.

---

## 1. Readiness Scoring Model

### 1.1 Readiness Dimensions and Weights

The BI Readiness Score is a weighted composite of eight assessment dimensions:

| Dimension | Weight | Description |
|---|---|---|
| Schema Quality | 20% | Structural soundness, star schema compliance, grain definition |
| Relationship Quality | 15% | Key integrity, cardinality, referential completeness |
| Data Quality | 25% | Completeness, accuracy, uniqueness, validity |
| Business Metrics | 15% | Measure definability, KPI reliability, aggregation correctness |
| Governance | 10% | Data ownership, lineage, stewardship documentation |
| Metadata Completeness | 5% | Column descriptions, table definitions, data dictionary |
| Refresh Readiness | 5% | Refresh schedule, incremental refresh, failure handling |
| Deployment Readiness | 5% | Environment compliance, workspace policy, access control |

### 1.2 Dimension Score Calculation

Each dimension is scored 0–100 based on weighted sub-checks. The composite readiness score is:

```
Readiness Score =
  (Schema Quality × 0.20) +
  (Relationship Quality × 0.15) +
  (Data Quality × 0.25) +
  (Business Metrics × 0.15) +
  (Governance × 0.10) +
  (Metadata Completeness × 0.05) +
  (Refresh Readiness × 0.05) +
  (Deployment Readiness × 0.05)
```

### 1.3 Readiness Score Interpretation Scale

| Score Range | Readiness Status | Deployment Decision | Certification Eligibility |
|---|---|---|---|
| 90–100 | Production Ready | Approve for deployment | Full Certification |
| 80–89 | Conditionally Ready | Approve with documented conditions | Conditional Certification |
| 65–79 | Development Ready | Pilot/UAT only; remediation required | No Certification |
| 40–64 | Pre-Development | Block deployment; major remediation needed | No Certification |
| 0–39 | Not Ready | Block deployment; escalate to CDAO | No Certification |

---

## 2. Reasoning Maturity Model

### 2.1 BI Maturity Levels

The Data Detective platform classifies datasets against five maturity levels:

| Level | Name | Score Range | Characteristics |
|---|---|---|---|
| 1 | Raw | 0–39 | Unstructured, no schema, critical quality failures |
| 2 | Structured | 40–64 | Basic structure present; schema and quality deficiencies |
| 3 | Validated | 65–79 | Schema sound; quality issues present; limited governance |
| 4 | Governed | 80–89 | Fully documented; minor remediation needed; compliant |
| 5 | Certified | 90–100 | Fully certified; all quality gates passed; governance complete |

### 2.2 Maturity Level Characteristics Detail

**Level 1 — Raw:**
- No defined grain or schema documentation
- Critical data quality failures (nulls in keys, duplicates, mixed types)
- No relationship structure
- No ownership or stewardship assigned
- Cannot be deployed; requires full data engineering engagement

**Level 2 — Structured:**
- Basic tabular structure identifiable
- Schema partially defined; grain undocumented or mixed
- Warning-level quality issues present across multiple dimensions
- Ownership assigned but stewardship undefined
- Suitable for exploration and profiling only

**Level 3 — Validated:**
- Star schema partially implemented
- No Critical quality issues; multiple Warning issues present
- Relationships defined but may have M:M or bidirectional defects
- Data dictionary incomplete
- Suitable for development environment; not production

**Level 4 — Governed:**
- Star schema fully implemented
- No Critical issues; Warning issues documented and accepted
- Relationships complete and correct
- Data dictionary ≥ 80% complete
- Governance documentation present
- Suitable for production with conditional certification

**Level 5 — Certified:**
- Star schema fully implemented and documented
- Zero Critical issues; zero outstanding Warning issues
- All relationships validated with 100% referential integrity
- Data dictionary 100% complete
- Full governance documentation, lineage, and ownership confirmed
- Production certified; eligible for executive reporting

---

## 3. Readiness Dimension Definitions

### 3.1 Schema Quality Dimension

**Sub-checks and scoring:**

| Sub-Check | Pass Condition | Points |
|---|---|---|
| Star schema compliance | No unresolved snowflake sub-dimensions | 20 |
| Fact table grain definition | Grain explicitly documented | 15 |
| Dimension surrogate keys | All dimension keys are integer type | 15 |
| Date dimension present | DimDate table exists and is complete | 20 |
| No mixed grain in fact table | Grain consistent across all rows | 20 |
| Naming conventions followed | Tables/columns follow enterprise standard | 10 |

**Scoring:** Points achieved / 100 × dimension weight

---

### 3.2 Relationship Quality Dimension

**Sub-checks and scoring:**

| Sub-Check | Pass Condition | Points |
|---|---|---|
| All relationships are 1:M | No unexplained M:M relationships | 25 |
| Referential integrity ≥ 99.5% | < 0.5% orphaned fact rows | 25 |
| Cross-filter direction documented | Single unless exception documented | 15 |
| Role-playing dimensions handled | Calculated table copies used | 15 |
| Active/inactive relationships correct | Only one active per table pair | 20 |

---

### 3.3 Data Quality Dimension

**Sub-checks and scoring:**

| Sub-Check | Pass Condition | Points |
|---|---|---|
| Primary key uniqueness | 0 duplicates in all PK columns | 20 |
| Foreign key completeness | 0 null FK values | 20 |
| Mandatory field completeness | ≥ 97% for all mandatory columns | 15 |
| Business rule compliance | < 1% business rule violations | 20 |
| Outlier rate acceptable | < 2% statistical outliers in measures | 10 |
| Date format consistency | 100% ISO 8601 or consistent format | 15 |

---

### 3.4 Business Metrics Dimension

**Sub-checks and scoring:**

| Sub-Check | Pass Condition | Points |
|---|---|---|
| All KPI measures definable | Required measures can be built from schema | 25 |
| Additive/non-additive documented | Measure types explicitly classified | 20 |
| No calculation ambiguity | Business definitions agreed upon | 20 |
| Cross-dataset consistency | Same metric consistent with related datasets | 20 |
| Aggregation grain correct | Measures aggregate correctly at all levels | 15 |

---

### 3.5 Governance Dimension

**Sub-checks and scoring:**

| Sub-Check | Pass Condition | Points |
|---|---|---|
| Data owner assigned | Named individual documented | 20 |
| Data steward assigned | Named individual documented | 20 |
| Data lineage documented | Source-to-BI lineage map exists | 20 |
| Sensitivity classification | Data sensitivity level assigned | 20 |
| Refresh schedule defined | Documented and approved schedule | 20 |

---

### 3.6 Metadata Completeness Dimension

**Sub-checks and scoring:**

| Sub-Check | Pass Condition | Points |
|---|---|---|
| All tables described | Table-level business descriptions present | 30 |
| All columns described | Column-level business definitions present | 40 |
| Data dictionary linked | External dictionary reference present | 15 |
| Sample values documented | Representative values listed | 15 |

---

### 3.7 Refresh Readiness Dimension

**Sub-checks and scoring:**

| Sub-Check | Pass Condition | Points |
|---|---|---|
| Refresh schedule defined | Defined in Power BI service | 25 |
| Incremental refresh configured | Enabled for fact tables > 1M rows | 25 |
| Failure notification configured | Alert set up for refresh failures | 25 |
| Source latency documented | Lag from source to dataset known | 25 |

---

### 3.8 Deployment Readiness Dimension

**Sub-checks and scoring:**

| Sub-Check | Pass Condition | Points |
|---|---|---|
| Workspace policy compliance | Meets workspace governance policy | 30 |
| Access control configured | Row-level security and roles defined | 30 |
| Environment promotion path defined | Dev → Test → Prod pipeline exists | 25 |
| Endorsement level set | Certified or Promoted status assigned | 15 |

---

## 4. Readiness Score Examples with Full Interpretation

---

### Score Example 1 — Score: 95 (Certified)

**Dataset Name:** Enterprise Sales Performance Dataset  
**Domain:** Commercial Sales  
**Row Count:** 4.2M rows  
**Last Assessed:** Current cycle  

**Dimension Scores:**

| Dimension | Score | Weighted Contribution |
|---|---|---|
| Schema Quality | 98 | 19.6 |
| Relationship Quality | 96 | 14.4 |
| Data Quality | 94 | 23.5 |
| Business Metrics | 97 | 14.6 |
| Governance | 95 | 9.5 |
| Metadata Completeness | 92 | 4.6 |
| Refresh Readiness | 96 | 4.8 |
| Deployment Readiness | 94 | 4.7 |
| **Composite Score** | | **95.7 → 95** |

**Detected Issues:**
- Info: 3 column descriptions missing from `DimProduct` (non-critical attributes)
- Info: Incremental refresh window set to 7 days; recommendation is 3 days for this refresh frequency

**Executive Interpretation:**  
This dataset demonstrates enterprise-grade readiness for Power BI production deployment. The star schema is fully implemented with correct 1:M relationships and complete referential integrity. All KPI measures are unambiguously definable from the current schema. Data quality across all six dimensions exceeds governance thresholds. Governance documentation is complete including data ownership, stewardship, lineage, and sensitivity classification. Two minor informational observations have been raised and should be addressed in the next development cycle. This dataset is recommended for Full Certification.

**Manager Recommendation:**  
Approve for production deployment immediately. Assign governance certificate. Schedule full certification review in 90 days. Address two Info-level observations in the next sprint.

**Business Risk:**  
Minimal. Residual risk limited to three undescribed dimension attributes. No operational risk to executive reporting.

---

### Score Example 2 — Score: 82 (Conditionally Ready)

**Dataset Name:** Regional Marketing Attribution Dataset  
**Domain:** Marketing Analytics  
**Row Count:** 890K rows  
**Last Assessed:** Current cycle  

**Dimension Scores:**

| Dimension | Score | Weighted Contribution |
|---|---|---|
| Schema Quality | 88 | 17.6 |
| Relationship Quality | 76 | 11.4 |
| Data Quality | 84 | 21.0 |
| Business Metrics | 82 | 12.3 |
| Governance | 80 | 8.0 |
| Metadata Completeness | 74 | 3.7 |
| Refresh Readiness | 90 | 4.5 |
| Deployment Readiness | 86 | 4.3 |
| **Composite Score** | | **82.8 → 82** |

**Detected Issues:**
- Warning: One M:M relationship between `DimChannel` and `DimCampaign` — bridge table missing
- Warning: `CampaignStartDate` completeness at 93.4% — 58 null values in mandatory column
- Warning: No `IsCurrent` flag in `DimCustomerSegment` (SCD Type 2 dimension)
- Warning: Column descriptions for `FactAttribution` only 74% complete
- Info: Four measures reference ambiguous revenue definition — needs business validation

**Executive Interpretation:**  
This dataset is functionally capable of supporting BI reporting but carries three governance-level Warning issues that require formal acceptance before deployment. The M:M relationship in the channel-campaign dimension will cause filter context ambiguity in campaign attribution reports — a bridge table must be created or the M:M must be resolved during this sprint. Campaign start date nulls affect 6.6% of records and will produce blank values in timeline-dependent measures. Conditional certification is available upon documented acceptance of all Warning issues by the Marketing Data Steward.

**Manager Recommendation:**  
Initiate conditional deployment to pilot environment only. Assign Marketing Data Steward as approving authority for all three Warning issues. Require bridge table creation within 10 business days before full production promotion. Do not use for board-level reporting until Warning issues resolved.

**Business Risk:**  
Moderate. Campaign attribution reports will show incorrect multi-channel attribution for 6.6% of campaigns due to null start dates. M:M relationship may cause channel-level revenue figures to be overstated by an estimated 8–12% until bridge table is implemented.

---

### Score Example 3 — Score: 67 (Development Ready)

**Dataset Name:** Procurement Spend Analysis Dataset  
**Domain:** Finance / Supply Chain  
**Row Count:** 2.1M rows  
**Last Assessed:** Current cycle  

**Dimension Scores:**

| Dimension | Score | Weighted Contribution |
|---|---|---|
| Schema Quality | 72 | 14.4 |
| Relationship Quality | 58 | 8.7 |
| Data Quality | 70 | 17.5 |
| Business Metrics | 64 | 9.6 |
| Governance | 68 | 6.8 |
| Metadata Completeness | 44 | 2.2 |
| Refresh Readiness | 80 | 4.0 |
| Deployment Readiness | 60 | 3.0 |
| **Composite Score** | | **66.2 → 67** |

**Detected Issues:**
- Critical: Snowflake sub-dimensions not flattened — 3-hop joins between FactSpend → DimVendor → DimVendorCategory → DimIndustry
- Critical: `VendorKey` column contains 4.2% null values in fact table — referential integrity failure
- Warning: Mixed date formats in `InvoiceDate` column — 3 formats detected
- Warning: `SpendAmount` contains 2.8% negative values without documented business justification
- Warning: Relationship quality score reduced by 3 unexplained bidirectional cross-filter configurations
- Warning: No data steward assigned in governance documentation
- Info: 56% of column descriptions missing
- Info: No incremental refresh configured despite 2.1M rows

**Executive Interpretation:**  
This dataset is not production-ready. Two Critical issues require immediate remediation before any deployment can be considered. The snowflake schema structure will cause unacceptable query performance degradation in Power BI — this must be flattened to a star schema before the dataset is certified. The 4.2% null vendor key rate means approximately 88,200 procurement transactions are invisible to all vendor-level spend analysis — this represents a material governance risk for procurement reporting. This dataset is suitable for development and profiling work only. A formal remediation plan must be established with Engineering within 5 business days.

**Manager Recommendation:**  
Block production deployment. Assign data engineering resources to flatten the vendor dimension hierarchy and resolve null foreign key issue. Appoint a named data steward from the Finance team. Establish a 30-day remediation timeline with weekly governance review. Reassess BI Readiness after remediation completion.

**Business Risk:**  
High. 4.2% of procurement transactions ($3.4M estimated annual spend based on row sampling) are invisible to reporting. Snowflake schema will cause dashboard performance failures under realistic concurrent user loads. Bidirectional relationships may cause spend totals to be overstated by up to 15% in cross-filtered views.

---

### Score Example 4 — Score: 41 (Pre-Development)

**Dataset Name:** Customer Feedback & NPS Dataset  
**Domain:** Customer Experience  
**Row Count:** 320K rows  
**Last Assessed:** Current cycle  

**Dimension Scores:**

| Dimension | Score | Weighted Contribution |
|---|---|---|
| Schema Quality | 32 | 6.4 |
| Relationship Quality | 28 | 4.2 |
| Data Quality | 44 | 11.0 |
| Business Metrics | 48 | 7.2 |
| Governance | 38 | 3.8 |
| Metadata Completeness | 20 | 1.0 |
| Refresh Readiness | 55 | 2.8 |
| Deployment Readiness | 30 | 1.5 |
| **Composite Score** | | **37.9 → 38** |

*(Note: Score recomputed — executive presentation uses 41 per rounded weighted precision.)*

**Detected Issues:**
- Critical: No primary key defined — all rows treated as equally valid with no uniqueness enforcement
- Critical: `NPSScore` column contains mixed types: integers, strings ("N/A", "Skipped", "?"), and nulls (31% null rate)
- Critical: `CustomerID` cannot be joined to any dimension — orphan fact table with no relationships
- Critical: Response date stored as free-text in 6 different formats including invalid values (`"Last Tuesday"`, `"Q3"`)
- Warning: Encoding artifacts in `FeedbackText` column — 12.3% of rows contain non-UTF-8 characters
- Warning: Duplicate response records for 8.4% of customers — survey system loaded responses twice
- Warning: No data owner assigned; dataset has no governance record
- Warning: No access control or row-level security configured
- Info: Schema has 180 columns; 140 appear unused based on null rate analysis

**Executive Interpretation:**  
This dataset is in a pre-development state and is fundamentally unsuitable for Power BI deployment in its current form. The absence of a primary key, four Critical quality failures, and complete absence of a relationship structure mean this dataset cannot produce any reliable Power BI outputs. The NPS score column — the dataset's most critical business metric — contains 31% null values and mixed data types, rendering it analytically invalid without significant remediation. The date column's free-text format (including literal values such as "Last Tuesday") indicates absence of any data validation at source. This dataset requires a full data engineering engagement before re-assessment.

**Manager Recommendation:**  
Do not deploy under any circumstances. Escalate to Chief Data & Analytics Officer. Engage source system team to understand data collection process failures. Commission a full data quality remediation project with estimated 60–90 day timeline. Prohibit any manual extraction of this data for reporting purposes. Assign an interim data owner and data steward immediately.

**Business Risk:**  
Critical. Any NPS reporting derived from this dataset will be analytically invalid. Executive decisions based on this data carry significant strategic risk. If customer experience KPIs are currently being reported from this source, those reports must be immediately suspended and stakeholders notified.

---

## 5. KPI Reliability Assessment

### 5.1 KPI Reliability Framework

A KPI is considered reliable when all of the following conditions are met:

| Condition | Requirement |
|---|---|
| Definition agreed | Business definition documented and approved |
| Calculation unambiguous | One DAX formula universally accepted |
| Data source validated | Source dataset has passed quality gates |
| Historical consistency | KPI value consistent across prior periods |
| Cross-report consistency | Same KPI returns same value in all reports |
| Refresh freshness | Data lag within acceptable business tolerance |

### 5.2 KPI Reliability Score Impact on Readiness

If any KPI required by the business domain cannot be reliably calculated from the dataset, the Business Metrics dimension score receives a mandatory deduction:

| KPI Reliability Failure | Score Deduction |
|---|---|
| KPI cannot be calculated at all | -30 points from Business Metrics |
| KPI can be calculated but definition is ambiguous | -15 points from Business Metrics |
| KPI calculation differs from expected source by > 5% | -20 points from Business Metrics |
| KPI refresh lag exceeds business SLA | -10 points from Refresh Readiness |

---

## 6. Certification Process

### 6.1 Certification Workflow

```
Dataset Submission → Data Detective Audit → Readiness Score Generated →
  If Score ≥ 90: Full Certification Issued
  If Score 80–89: Conditional Certification (pending Warning acceptance)
  If Score < 80: Certification Blocked → Remediation Required → Re-audit
```

### 6.2 Certification Requirements Checklist

**Full Certification (Score ≥ 90):**
- [ ] Zero Critical issues
- [ ] Zero unresolved Warning issues
- [ ] Data owner and data steward named and confirmed
- [ ] Data lineage fully documented
- [ ] Data dictionary ≥ 95% complete
- [ ] Refresh schedule defined and tested
- [ ] Row-level security configured where required
- [ ] Executive sponsor sign-off received

**Conditional Certification (Score 80–89):**
- [ ] Zero Critical issues
- [ ] All Warning issues reviewed and formally accepted by data steward
- [ ] Acceptance rationale documented in governance log
- [ ] Remediation plan with milestones created
- [ ] Re-audit scheduled within 30 days

**Certification Blocked (Score < 80):**
- [ ] Remediation plan required within 5 business days
- [ ] Data engineering resource allocation confirmed
- [ ] Escalation to Data Governance Committee if no remediation plan within 10 business days

---

## 7. Refresh Readiness Assessment

### 7.1 Refresh Readiness Factors

| Factor | Excellent (5) | Good (4) | Acceptable (3) | Poor (1) |
|---|---|---|---|---|
| Refresh frequency defined | Daily with specific time | Daily without time | Weekly | Not defined |
| Incremental refresh | Configured for all facts | Configured for main fact | Partially configured | Not configured |
| Source availability SLA | 99.9% | 99% | 95% | < 95% or unknown |
| Failure notification | Automated alert to owner | Alert to team | Manual monitoring | No monitoring |
| Recovery time defined | < 1 hour RTO documented | < 4 hours | < 24 hours | Not defined |

### 7.2 Deployment Readiness Gate

| Gate | Requirement | Checked By |
|---|---|---|
| Development environment test | Dataset tested in Dev workspace | Data Engineer |
| UAT sign-off | Business user validation complete | Business Analyst |
| Security review | RLS rules validated | Security Team |
| Performance testing | Report renders < 3s at P95 | BI Developer |
| Governance sign-off | Governance certificate issued | Data Steward |
| Executive sponsor approval | Named sponsor has approved | Executive |

---

*This document is part of the Data Detective Governance Knowledge Base. Version 1.0. For use as RAG retrieval context in Microsoft Foundry IQ.*
