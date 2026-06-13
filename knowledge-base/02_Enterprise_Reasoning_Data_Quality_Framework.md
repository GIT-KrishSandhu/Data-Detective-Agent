# 02 — Enterprise Reasoning Data Quality Framework
## Authoritative Reference for Data Detective Quality Agent

---

## Executive Summary

Data quality is not a technical concern — it is a business risk. Every quality defect that reaches a Power BI dashboard has the potential to distort executive decisions, invalidate KPI reporting, trigger regulatory scrutiny, and erode organizational trust in Business Intelligence. This framework defines the reasoning model, detection taxonomy, severity hierarchy, remediation strategies, and governance policies that the Data Detective Quality Agent uses to audit datasets before deployment to Power BI. Every issue category includes structured examples suitable for RAG retrieval and executive summary generation.

---

## 1. The Six Dimensions of Data Quality

### 1.1 Completeness

**Definition:** The degree to which required data values are present and non-null across all records and columns.

**Completeness Threshold Standards:**

| Column Criticality | Minimum Completeness | Action if Below |
|---|---|---|
| Primary Key | 100% | Block deployment |
| Foreign Key | 100% | Block deployment |
| Business Measure | ≥ 99% | Critical issue |
| Mandatory Attribute | ≥ 97% | Warning issue |
| Optional Attribute | ≥ 80% | Info issue |

**Detection Formula:** `Completeness% = (Non-null Count / Total Row Count) × 100`

---

### 1.2 Accuracy

**Definition:** The degree to which data correctly represents the real-world entity or event it is intended to model.

**Accuracy checks include:**
- Values within domain-valid ranges (e.g., Age between 0 and 120)
- Referential integrity between related datasets
- Business-rule cross-validation (e.g., `ShipDate >= OrderDate`)
- Statistical outlier detection against established baselines

---

### 1.3 Consistency

**Definition:** The degree to which the same data entity is represented uniformly across all tables, systems, and time periods.

**Consistency failures include:**
- `Gender = "Male"` in one table and `Gender = "M"` in another
- `CountryCode = "AUS"` in one system and `CountryCode = "AU"` in another
- Revenue calculated as `NetAmount` in one report and `GrossAmount` in another

---

### 1.4 Uniqueness

**Definition:** The degree to which each record represents a distinct real-world entity with no unintentional duplication.

**Uniqueness checks:**
- Exact duplicates (all columns identical)
- Partial duplicates (key columns identical but non-key columns differ)
- Fuzzy duplicates (near-identical values in name/address columns)

---

### 1.5 Validity

**Definition:** The degree to which data values conform to defined business rules, formats, and allowed value domains.

**Validity checks include:**
- Date format conformance (`YYYY-MM-DD`)
- Regex pattern conformance (e.g., email format, postal codes)
- Allowed value list enforcement (e.g., `Status ∈ {Active, Inactive, Pending}`)
- Numeric range constraints (e.g., `Discount% ∈ [0, 100]`)

---

### 1.6 Integrity

**Definition:** The degree to which relationships between datasets are logically sound and referentially consistent.

**Integrity checks include:**
- All foreign key values exist in the referenced dimension table
- Parent records exist before child records (temporal integrity)
- Aggregated totals reconcile with transactional detail

---

## 2. Severity Definitions

### 2.1 Critical Severity

**Definition:** A defect that, if unresolved, will cause materially incorrect Power BI outputs that cannot be manually corrected by report consumers.

**Critical issues block deployment.**

**Critical criteria:**
- Primary or foreign key nulls or duplicates
- Mixed data types in key or measure columns
- Date values outside physically plausible range
- Completeness below 90% for mandatory business measures
- Business rule violations affecting ≥ 5% of records
- Referential integrity failures ≥ 1% of fact rows

---

### 2.2 Warning Severity

**Definition:** A defect that will produce misleading or unreliable outputs for some report users under specific filter conditions.

**Warning issues must be documented and accepted by data owner before deployment.**

**Warning criteria:**
- Completeness 90–97% for mandatory attributes
- Inconsistent value encoding (e.g., mixed case, mixed codes)
- Outliers present in 0.1–5% of measure rows
- Schema drift detected relative to previous dataset version
- Non-integer surrogate keys in relationship columns
- SCD Type 2 dimensions missing `IsCurrent` flag

---

### 2.3 Info Severity

**Definition:** A defect or observation that reduces data richness, documentation completeness, or optimization potential but does not materially distort BI outputs.

**Info issues are flagged for awareness and future remediation planning.**

**Info criteria:**
- Optional attribute completeness 80–95%
- Suboptimal data types (e.g., float where integer is sufficient)
- Missing column descriptions or business definitions
- Unused columns detected in import
- Inconsistent naming conventions within a dataset

---

## 3. Issue Taxonomy with Examples

---

### Issue Category 1 — Missing Values

**Issue:** Null values in columns designated as mandatory  
**Detection:** `df[col].isnull().sum() / len(df) > threshold`  
**Analysis:** Nulls in foreign key columns cause orphaned fact rows silently excluded from Power BI measures  
**Recommendation:** Impute using domain rules (e.g., default category), flag for source system investigation, or reject rows during ETL  
**Business Impact:** Orphaned rows represent invisible revenue — executive dashboards understate performance by the amount attached to orphaned records

---

### Issue Category 2 — Duplicate Records (Exact)

**Issue:** Identical rows appearing multiple times in a fact or dimension table  
**Detection:** `df.duplicated().sum() > 0` (exact); composite key group-by count > 1  
**Analysis:** Duplicate rows cause SUM measures to double-count; duplicate dimension rows cause fan-out in joins  
**Recommendation:** Deduplicate at ETL layer; add UNIQUE constraint at source; investigate ETL pipeline for double-load events  
**Business Impact:** Revenue overstatement; headcount inflation; compliance reporting inaccuracy

**Example:**

| OrderID | CustomerKey | Revenue | Loaded At |
|---|---|---|---|
| ORD-1042 | 5231 | 4,200 | 2024-03-01 08:02 |
| ORD-1042 | 5231 | 4,200 | 2024-03-01 08:04 |

*Two identical rows loaded 2 minutes apart — ETL pipeline ran twice due to retry logic.*

---

### Issue Category 3 — Partial Duplicates (Key Collision)

**Issue:** Same primary key value with conflicting attribute values  
**Detection:** Group by key columns; check count > 1 with distinct non-key values  
**Analysis:** Indicates source system data merge conflict or SCD handling failure  
**Recommendation:** Implement a conflict resolution rule (latest record wins, or audit required); escalate to data steward  
**Business Impact:** Customer dimension returns ambiguous results for specific CustomerKey values — filter context resolves to incorrect attribute

**Example:**

| CustomerKey | CustomerName | Region |
|---|---|---|
| 5231 | Northbrook Industries | APAC |
| 5231 | Northbrook Industries Ltd | EMEA |

*Same key, different names and regions — conflict from CRM data merge.*

---

### Issue Category 4 — Mixed Data Types

**Issue:** A column contains values of different data types within the same column  
**Detection:** `df[col].apply(type).nunique() > 1` or `pd.to_numeric(df[col], errors='coerce').isnull()` count  
**Analysis:** Mixed types prevent correct aggregation; Power BI will either coerce or error on import  
**Recommendation:** Standardize column type at source; add explicit type cast in Power Query  
**Business Impact:** Revenue column stored as mixed int/string causes SUM to return null for entire column

**Example:**

| Row | UnitPrice |
|---|---|
| 1 | 149.99 |
| 2 | "N/A" |
| 3 | 220.00 |
| 4 | None |
| 5 | 175 |

*Mixed float, string, and null values in a pricing column — ETL did not enforce type.*

---

### Issue Category 5 — Outliers

**Issue:** Numeric values statistically improbable given the column's known distribution  
**Detection:** IQR method: `Q1 - 1.5×IQR` and `Q3 + 1.5×IQR`; Z-score > ±3  
**Analysis:** Outliers may be legitimate (large enterprise deal) or erroneous (data entry error, unit conversion failure)  
**Recommendation:** Flag for business validation; do not auto-remove without data owner confirmation; document in quality report  
**Business Impact:** A single revenue outlier of $42M (actual: $42K — unit conversion error) distorts average deal size KPI by 340%

---

### Issue Category 6 — Date Format Inconsistency

**Issue:** Date values stored in multiple formats within the same column  
**Detection:** Attempt parse with multiple format patterns; detect rows where primary format fails  
**Analysis:** Power BI cannot join inconsistent date formats to DimDate; temporal measures fail for affected rows  
**Recommendation:** Standardize to ISO 8601 (`YYYY-MM-DD`) at source or in ETL; apply `pd.to_datetime(errors='coerce')` with explicit format  
**Business Impact:** 12% of sales records excluded from time-intelligence measures due to non-standard date format

**Example:**

| OrderDate |
|---|
| 2024-03-15 |
| 15/03/2024 |
| March 15, 2024 |
| 20240315 |
| 03-15-24 |

*Five different date formats in one column from a multi-system data merge.*

---

### Issue Category 7 — Encoding Problems

**Issue:** Non-UTF-8 characters causing garbled text in dimension attribute columns  
**Detection:** `df[col].str.encode('utf-8', errors='replace').str.decode('utf-8') != df[col]`  
**Analysis:** Encoding artifacts in customer names or product descriptions break slicer display and search functionality  
**Recommendation:** Enforce UTF-8 encoding at source extract; apply `str.encode().decode()` normalization in ETL  
**Business Impact:** Customer names display as `Müller GmbH` → `M�ller GmbH`; slicer search broken for 340 affected customers

---

### Issue Category 8 — Null Handling in Measures

**Issue:** Null values in measure columns that are implicitly treated as 0 in SUM aggregations  
**Detection:** `df[measure_col].isnull().any()`; check if null count is material  
**Analysis:** `SUM` ignores nulls; `AVERAGE` excludes nulls from denominator — both behaviors can be correct or incorrect depending on business definition  
**Recommendation:** Explicitly define null handling in business rules: null = not applicable (exclude) vs. null = zero (include)  
**Business Impact:** Customer satisfaction score averages calculated excluding 23% of null-response records — average biased upward

---

### Issue Category 9 — Schema Drift

**Issue:** Column added, removed, or renamed between dataset versions without notification  
**Detection:** Compare column sets between current and prior version; flag additions, deletions, type changes  
**Analysis:** Power BI semantic model breaks when source columns are removed or renamed; silently produces empty visuals  
**Recommendation:** Version control schema with `schema_version` metadata; require change notification to BI team before source modifications  
**Business Impact:** Production dashboard shows blank visuals for 3 days after source system upgrade — undetected until executive presentation

---

### Issue Category 10 — Referential Integrity Failures

**Issue:** Foreign key values in fact table do not exist in referenced dimension table  
**Detection:** Anti-join: `fact_df[~fact_df['CustomerKey'].isin(dim_df['CustomerKey'])]`  
**Analysis:** Orphaned fact rows silently excluded from all measures — these rows exist but are invisible to Power BI  
**Recommendation:** Implement a default "Unknown" dimension member; investigate source ETL for missing dimension population logic  
**Business Impact:** $1.4M in transaction revenue assigned to customers not in DimCustomer — invisible to all revenue reports

---

### Issue Category 11 — Business Rule Violations

**Issue:** Data violates defined business logic constraints  
**Detection:** Rule-based validation queries: `df[df['ShipDate'] < df['OrderDate']]`  
**Analysis:** Violated rules indicate source system data entry errors, ETL transformation bugs, or system clock issues  
**Recommendation:** Define all business rules in a validation rule registry; apply during ETL load; reject or quarantine violating rows  
**Business Impact:** Logistics reports show negative lead times for 1.2% of orders — SLA compliance metrics appear artificially favorable

**Business Rule Violation Examples:**

| Rule ID | Rule Description | Violation Example |
|---|---|---|
| BR-001 | ShipDate >= OrderDate | ShipDate = 2024-01-10, OrderDate = 2024-01-15 |
| BR-002 | Discount% ∈ [0, 100] | Discount% = -5 or Discount% = 150 |
| BR-003 | Quantity > 0 | Quantity = -3 |
| BR-004 | UnitPrice > 0 | UnitPrice = 0 for non-complimentary item |
| BR-005 | ReturnDate > PurchaseDate | ReturnDate < PurchaseDate |
| BR-006 | Age ∈ [0, 120] | Age = 999 (default placeholder) |
| BR-007 | SalaryAmount > 0 | SalaryAmount = -45000 |
| BR-008 | InvoiceTotal = SUM(LineItems) | InvoiceTotal ≠ line item sum by $0.01 |

---

### Issue Category 12 — Identifier Quality

**Issue:** Identifier columns (primary keys, natural keys) contain formatting inconsistencies  
**Detection:** Regex pattern analysis; length distribution; character set analysis  
**Analysis:** Inconsistent identifiers break joins silently; records appear orphaned when they are not  
**Recommendation:** Normalize identifiers at source; apply consistent formatting rules before ETL load  
**Business Impact:** `CustomerID = "CUST-0042"` in orders table vs `CustomerID = "cust-42"` in returns table — join fails for 8% of records

---

### Issue Category 13 — Placeholder / Sentinel Values

**Issue:** Missing data indicated by placeholder values instead of null  
**Detection:** Value frequency analysis; identify suspicious high-frequency values like 0, -1, 9999, "N/A", "Unknown", "TBD"  
**Analysis:** Placeholders are treated as real values by Power BI — distorting aggregations, averages, and filters  
**Recommendation:** Map sentinel values to true nulls during ETL; document all known sentinel values per column  
**Business Impact:** Average customer age of 34.2 years skewed to 67.4 years due to 9999 placeholder in Age column for 18% of customers

---

### Issue Category 14 — Temporal Gaps

**Issue:** Date ranges contain unexpected gaps indicating missing data loads  
**Detection:** Generate complete date spine; anti-join against actual dates present in data  
**Analysis:** Missing days/weeks cause time-intelligence measures (WoW, MoM, YTD) to produce incorrect results  
**Recommendation:** Identify missing load windows; backfill or document expected gaps (e.g., weekends, holidays)  
**Business Impact:** Week-over-week revenue comparison shows -100% for missing week followed by +200% for catch-up week — executive interpretation misleading

---

### Issue Category 15 — Case Inconsistency in Categorical Columns

**Issue:** Same categorical value represented with different capitalization  
**Detection:** `df[col].str.upper().value_counts()` compared to `df[col].value_counts()`  
**Analysis:** "ACTIVE", "Active", "active" treated as 3 distinct values — slicer and GROUP BY produce fragmented results  
**Recommendation:** Apply `str.title()` or `str.upper()` normalization; enforce allowed value list  
**Business Impact:** Customer status slicer shows 6 values instead of 3; users filter to "Active" and miss "ACTIVE" records — 34% of active customers invisible

---

### Issue Category 16 — Leading and Trailing Whitespace

**Issue:** String columns contain invisible leading or trailing space characters  
**Detection:** `(df[col] != df[col].str.strip()).sum() > 0`  
**Analysis:** `"Northbrook "` ≠ `"Northbrook"` — joins fail, slicer shows duplicate entries  
**Recommendation:** Apply `str.strip()` to all string columns as a default ETL step  
**Business Impact:** 240 customer dimension entries duplicated in slicer due to trailing space — user confusion, double-clicking attempts

---

### Issue Category 17 — Numeric Precision Loss

**Issue:** Financial values stored as floating-point with precision errors  
**Detection:** `df[col] - df[col].round(2) != 0`; check for values like `149.999999999`  
**Analysis:** Financial calculations with float precision errors accumulate — totals reconciliation fails by small amounts  
**Recommendation:** Store financial values as `DECIMAL(18,2)` at source; use Python `Decimal` type for ETL calculations  
**Business Impact:** Revenue totals differ by $0.03 from general ledger — triggers audit query; wastes 6 hours of finance team time

---

### Issue Category 18 — Duplicate Column Names After Case Normalization

**Issue:** Columns named `CustomerID` and `customerid` in same table after system merge  
**Detection:** `[c.lower() for c in df.columns]` with duplicate detection  
**Analysis:** Power Query treats both as valid columns; downstream calculations may reference wrong column  
**Recommendation:** Enforce unique column names (case-insensitive) in schema definition  
**Business Impact:** Revenue measure silently references wrong `customerid` column — customer-level revenue breakdown incorrect

---

### Issue Category 19 — Invalid Email Format

**Issue:** Email address column contains values not conforming to RFC 5322 format  
**Detection:** Regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`  
**Analysis:** Invalid emails break CRM integration; Power BI reports filtering by email fail for invalid values  
**Recommendation:** Apply regex validation at source data entry; flag invalid emails for customer data remediation  
**Business Impact:** 4.2% of marketing campaign emails undeliverable — campaign performance metrics understated

---

### Issue Category 20 — Currency Code Inconsistency

**Issue:** Revenue stored in multiple currencies without currency code column  
**Detection:** Column existence check; check for currency symbol embedded in numeric values  
**Analysis:** Multi-currency revenue summed in Power BI as if same currency — grossly inflated or deflated totals  
**Recommendation:** Add `CurrencyCode` column; apply exchange rate conversion in ETL before loading to fact table  
**Business Impact:** International division revenue reported in local currency summed with USD figures — executive sees $14.2M instead of $9.8M actual

---

### Issue Category 21 — Null Foreign Keys in Fact Table

**Issue:** Foreign key columns in fact table contain null values  
**Detection:** `df[fk_col].isnull().sum() > 0`  
**Analysis:** Null foreign keys cannot join to any dimension member — rows silently excluded from all dimension-filtered measures  
**Recommendation:** Implement `-1` unknown dimension member as default; replace nulls with `-1` during ETL  
**Business Impact:** 1.8% of transaction rows with null ProductKey invisible to all product-level revenue analysis

---

### Issue Category 22 — Column Count Explosion (Schema Bloat)

**Issue:** Dataset contains 200+ columns, majority with high null rates  
**Detection:** Column count > 100 combined with null rate analysis per column  
**Analysis:** Excessive columns increase ETL processing time, VertiPaq memory, and governance complexity  
**Recommendation:** Profile all columns; eliminate columns with > 95% null rate or 0 downstream usage  
**Business Impact:** 340-column dataset reduced to 87 columns after profiling — refresh time reduced 58%

---

### Issue Category 23 — Negative Values in Additive Measures

**Issue:** Additive measure columns (Revenue, Units) contain negative values without business justification  
**Detection:** `df[measure_col].lt(0).sum() > 0`  
**Analysis:** Negative values may represent returns/credits (valid) or data entry errors (invalid) — business rule needed  
**Recommendation:** Document business definition; separate returns into dedicated fact table if volume is significant  
**Business Impact:** Revenue total understated when returns mixed with sales without clear separation — P&L reporting distorted

---

### Issue Category 24 — Date Range Exceeding Business Reality

**Issue:** Date values exist outside the plausible operating range of the business  
**Detection:** `df[date_col].min() < business_start_date` or `df[date_col].max() > today + 5 years`  
**Analysis:** Future-dated orders or pre-business-existence records indicate data corruption or system default dates  
**Recommendation:** Apply date boundary validation: `[1970-01-01, today + 1 year]` as standard range  
**Business Impact:** `OrderDate = 2099-12-31` (system default) causes record to appear in all future time-intelligence windows

---

### Issue Category 25 — Surrogate Key Type Mismatch

**Issue:** Surrogate key defined as Integer in dimension but as Text in fact table (or vice versa)  
**Detection:** `dim_df['CustomerKey'].dtype != fact_df['CustomerKey'].dtype`  
**Analysis:** Type mismatch prevents Power BI relationship establishment; all cross-table measures return blank  
**Recommendation:** Enforce consistent data types for all join columns across all tables; validate in Data Detective pre-load  
**Business Impact:** Entire semantic model relationship graph breaks — all cross-table measures return blank for 100% of users

---

## 4. Root Cause Analysis Framework

### 4.1 Common Root Causes by Issue Category

| Root Cause | Associated Issues | Prevention |
|---|---|---|
| ETL pipeline retry without deduplication | Exact duplicates | Idempotent load logic |
| Source system data entry validation absent | Business rule violations, outliers | Source-level validation |
| Multi-system data merge without normalization | Case inconsistency, encoding issues, mixed types | Normalization layer |
| Schema change without communication | Schema drift | Change notification protocol |
| Missing dimension member management | Null foreign keys, referential integrity | Unknown member pattern |
| Currency/unit heterogeneity | Currency inconsistency, unit conversion | Standardization at source |
| Placeholder values for missing data | Sentinel values | Null handling standard |
| Date format heterogeneity from multiple sources | Date format inconsistency | ISO 8601 enforcement |

---

## 5. Governance Policies for Data Quality

### 5.1 Quality Gate Requirements

Before any dataset is approved for Power BI deployment, it must satisfy the following quality gates:

**Gate 1 — Critical Issues: Zero tolerance**
- [ ] Zero null primary keys
- [ ] Zero null foreign keys
- [ ] Zero exact duplicate primary keys
- [ ] Zero mixed data types in key or measure columns
- [ ] Zero referential integrity failures > 0.5%

**Gate 2 — Warning Issues: Documented acceptance**
- [ ] All warning issues reviewed by data steward
- [ ] Acceptance rationale documented in governance log
- [ ] Remediation plan created for deferred warnings

**Gate 3 — Info Issues: Acknowledged**
- [ ] Info issues logged in dataset quality report
- [ ] Remediation backlog item created where applicable

---

### 5.2 Remediation Escalation Matrix

| Severity | Owner | Resolution SLA | Escalation Path |
|---|---|---|---|
| Critical | Data Engineering | 24 hours | Data Engineering Manager → CDAO |
| Warning | Data Steward | 5 business days | BI Governance Committee |
| Info | Dataset Owner | Next refresh cycle | No escalation unless pattern repeats |

---

## 6. Data Quality Scoring Model

### 6.1 Composite Quality Score Calculation

```
Quality Score = (
  Completeness Weight × Completeness Score +
  Uniqueness Weight × Uniqueness Score +
  Validity Weight × Validity Score +
  Integrity Weight × Integrity Score +
  Consistency Weight × Consistency Score
)

Default Weights:
  Completeness: 25%
  Uniqueness:   20%
  Validity:     20%
  Integrity:    25%
  Consistency:  10%
```

### 6.2 Quality Score Interpretation

| Score Range | Interpretation | Deployment Decision |
|---|---|---|
| 95–100 | Excellent quality | Deploy with certification |
| 85–94 | Good quality | Deploy with minor warnings documented |
| 70–84 | Acceptable with remediation | Deploy only with data steward sign-off |
| 50–69 | Poor quality | Block deployment; remediation required |
| < 50 | Critical quality failure | Block deployment; escalate to CDAO |

---

*This document is part of the Data Detective Governance Knowledge Base. Version 1.0. For use as RAG retrieval context in Microsoft Foundry IQ.*
