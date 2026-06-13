# 01 — Power BI Semantic Modeling Guide
## Enterprise Reference for Data Detective Governance Platform

---

## Executive Summary

A well-designed Power BI semantic model is the foundation of trustworthy Business Intelligence. Poor modeling decisions made before data reaches Power BI propagate into inaccurate KPIs, misleading dashboards, and costly executive misinterpretation. This document defines authoritative standards for Power BI semantic modeling, schema design, relationship architecture, and model health assessment. It serves as grounding context for the Data Detective multi-agent platform when generating BI Readiness reports and governance certificates.

---

## 1. Schema Architecture

### 1.1 Star Schema — The Gold Standard

The **star schema** is the recommended dimensional model for Power BI. It consists of one central fact table surrounded by denormalized dimension tables. Every relationship is a single-hop join from dimension to fact.

**Why star schema is mandatory for Power BI performance:**
- DAX engine (VertiPaq) is optimized for single-hop relationships
- Filter context propagates efficiently across one-to-many joins
- Aggregation and grouping operations are faster on wide, flat dimension tables
- Query folding in DirectQuery is maximized

**Star Schema Structure:**

| Component | Role | Cardinality |
|---|---|---|
| Fact table | Stores quantitative events/measures | Many rows |
| Dimension table | Stores descriptive attributes | Fewer rows |
| Surrogate key | Integer key linking fact to dimension | One per relationship |
| Date dimension | Dedicated calendar table | One per model |

**Canonical example:**

```
DimCustomer ──┐
DimProduct  ──┤──► FactSales ◄──── DimDate
DimRegion   ──┘
```

### 1.2 Snowflake Schema — When to Avoid It

A **snowflake schema** normalizes dimension tables into sub-dimensions. While it reduces storage redundancy in relational databases, it introduces multi-hop joins that degrade Power BI performance.

**Anti-pattern:** `FactSales → DimProduct → DimProductCategory → DimProductSubcategory`

**Impact:** DAX must resolve multiple relationship hops. Query performance degrades by 30–70% compared to a flattened star schema.

**Recommendation:** Flatten all snowflake sub-dimensions into a single wide dimension table before ingesting data into Power BI. This is a pre-processing responsibility and a Data Detective quality gate.

### 1.3 Galaxy Schema (Multi-Fact)

Enterprise models often contain multiple fact tables sharing conformed dimensions. This is acceptable when:
- Shared dimensions are identical across facts (conformed dimensions)
- Relationships are correctly bridged
- Role-playing dimensions are handled via calculated tables or view copies

---

## 2. Fact Tables

### 2.1 Fact Table Design Principles

A fact table records measurable business events. Every row represents one occurrence of a business process.

**Required characteristics:**
- Contains only foreign keys and numeric measures
- No descriptive text columns (these belong in dimensions)
- Grain must be explicitly defined and documented
- Grain must be consistent across all rows

**Fact Table Grain Examples:**

| Business Domain | Grain Definition |
|---|---|
| Sales | One row per order line item |
| Finance | One row per journal entry |
| HR | One row per employee per pay period |
| Logistics | One row per shipment event |
| Web Analytics | One row per session per day |

### 2.2 Fact Table Anti-Patterns

- **Mixed grain:** Some rows represent order headers, others represent line items — causes double-counting in aggregations
- **Descriptive columns in fact tables:** Storing product name in the fact table instead of the product dimension key
- **No surrogate keys:** Using natural keys (e.g., order numbers with alphanumeric formats) as relationship keys — causes join inefficiency
- **Wide fact tables:** Dozens of rarely used measure columns inflating cardinality

### 2.3 Types of Facts

| Type | Description | Example |
|---|---|---|
| Additive | Can be summed across all dimensions | Revenue, Units Sold |
| Semi-additive | Can be summed across some dimensions | Account Balance, Inventory |
| Non-additive | Cannot be summed meaningfully | Ratios, Percentages, Rates |

> **Warning:** Non-additive measures stored as plain numeric columns in fact tables will be incorrectly aggregated by Power BI's default SUM behavior. These must be wrapped in DAX measures with explicit aggregation logic.

---

## 3. Dimension Tables

### 3.1 Dimension Table Design Principles

Dimension tables provide the descriptive context for fact measurements.

**Required characteristics:**
- One surrogate key column (integer, auto-incrementing)
- One natural key column (the original business identifier)
- Descriptive attribute columns (text-based, low cardinality preferred)
- No calculated metrics or aggregations

**Dimension Quality Checklist:**
- [ ] Surrogate key defined and is an integer
- [ ] Natural key preserved for auditability
- [ ] No null values in key columns
- [ ] Consistent text casing (e.g., all Title Case or all UPPER)
- [ ] No leading/trailing spaces in text columns
- [ ] Attribute columns have clear, business-friendly names

### 3.2 Slowly Changing Dimensions (SCD)

| SCD Type | Behavior | Power BI Implication |
|---|---|---|
| Type 1 | Overwrite — no history preserved | Simple; current state only |
| Type 2 | New row per change — history preserved | Requires date range filtering in DAX |
| Type 3 | New column per change | Rarely used; clutters dimension |

**Recommendation:** Type 2 SCD must include `ValidFrom`, `ValidTo`, and `IsCurrent` columns. Data Detective flags datasets with customer or product dimensions that lack these columns when the business domain implies historical tracking.

---

## 4. Relationships

### 4.1 Relationship Architecture Rules

| Rule | Requirement |
|---|---|
| Direction | Single direction from dimension → fact |
| Cardinality | One-to-many (1:M) from dimension to fact |
| Active vs. Inactive | Only one active relationship per table pair |
| Cross-filter direction | Single (default); Bidirectional only when explicitly justified |

### 4.2 Role-Playing Dimensions

A role-playing dimension is a single dimension used multiple times in the same fact table under different semantic roles.

**Example:** A `DimDate` table plays three roles in `FactSales`:
- `OrderDate`
- `ShipDate`
- `DeliveryDate`

**Correct implementation:**
- Create three calculated table copies: `DimDate_Order`, `DimDate_Ship`, `DimDate_Delivery`
- Create one active and two inactive relationships
- Use `USERELATIONSHIP()` in DAX measures for inactive relationships

**Anti-pattern:** Creating three separate physical date tables with duplicate data — increases model size and maintenance burden.

### 4.3 Many-to-Many Relationships

Many-to-many (M:M) relationships indicate a data modeling defect in most cases.

**Legitimate M:M use case:** Budget allocation across multiple cost centers and departments.

**Problematic M:M cause:** Missing bridge table or incorrect grain definition.

> **Warning:** Power BI silently accepts M:M relationships but they introduce ambiguous filter propagation. Any dataset arriving at Data Detective with unexplained M:M relationships should receive a governance flag.

---

## 5. Measures vs. Calculated Columns

### 5.1 Decision Matrix

| Criteria | Measure | Calculated Column |
|---|---|---|
| Computed at | Query time | Refresh time |
| Storage | None (virtual) | Stored in VertiPaq |
| Context-aware | Yes (filter context) | No (row context only) |
| Use in slicers | No | Yes |
| Performance | Better for aggregations | Better for row-level attributes |

### 5.2 Measure Best Practices

- All measures must be stored in a dedicated **measure table** (a blank, hidden table created for organization)
- Measures must use explicit naming: `[Total Revenue]`, `[YTD Revenue]`, `[MoM Revenue %]`
- Every measure must have a format string defined
- Measures should include comments where DAX logic is non-trivial

### 5.3 Calculated Column Anti-Patterns

- Replicating measure logic as a calculated column (e.g., `Revenue = [Quantity] * [UnitPrice]` as a column in the fact table)
- Using calculated columns for measures that need filter context (this will always return wrong results)
- High-cardinality text calculated columns that inflate model size

---

## 6. Surrogate Keys and Primary Keys

### 6.1 Surrogate Key Standards

Surrogate keys are system-generated integer keys used exclusively for joining fact tables to dimension tables.

**Requirements:**
- Data type: Integer (INT or BIGINT)
- Uniqueness: No duplicates in dimension table
- Completeness: No nulls
- Stability: Values never change once assigned

**Natural Key vs. Surrogate Key:**

| Property | Natural Key | Surrogate Key |
|---|---|---|
| Source | Business system | Data warehouse |
| Type | Often string/composite | Integer |
| Join performance | Poor | Excellent |
| Stability | Changes with business rules | Never changes |

> **Executive Note:** Datasets arriving with string-based join keys (e.g., `CustomerCode = "CUST-AU-0042"`) are a leading cause of Power BI relationship inefficiency and VertiPaq memory bloat. Data Detective flags all non-integer relationship keys as a Warning severity issue.

---

## 7. Date Dimension

### 7.1 Date Dimension Requirements

Every Power BI semantic model must include a dedicated date dimension. Power BI's auto-generated date hierarchy is insufficient for enterprise models.

**Required columns in `DimDate`:**

| Column | Type | Example |
|---|---|---|
| DateKey | Integer (YYYYMMDD) | 20240315 |
| Date | Date | 2024-03-15 |
| DayOfWeek | Integer | 5 |
| DayName | Text | Friday |
| WeekNumber | Integer | 11 |
| MonthNumber | Integer | 3 |
| MonthName | Text | March |
| Quarter | Integer | 1 |
| QuarterName | Text | Q1 |
| Year | Integer | 2024 |
| FiscalYear | Integer | 2024 |
| FiscalQuarter | Integer | 3 |
| IsWeekend | Boolean | False |
| IsHoliday | Boolean | False |
| IsBusinessDay | Boolean | True |

### 7.2 Date Dimension Anti-Patterns

- Storing dates as text strings in fact tables (`"2024-03-15"`, `"15/03/2024"`)
- Missing the date dimension entirely and relying on Power BI Auto Date/Time
- Date dimension that does not cover the full range of fact table dates
- Fiscal calendar logic embedded in measures instead of the date dimension

---

## 8. Naming Conventions

### 8.1 Table Naming Standards

| Object Type | Prefix | Example |
|---|---|---|
| Fact Table | `Fact` | `FactSales`, `FactInventory` |
| Dimension Table | `Dim` | `DimCustomer`, `DimProduct` |
| Bridge Table | `Bridge` | `BridgeSalesTerritory` |
| Date Table | `DimDate` | `DimDate`, `DimDate_Ship` |
| Measure Table | `_Measures` | `_SalesMeasures` |

### 8.2 Column Naming Standards

- Use PascalCase: `CustomerName`, `OrderDate`, `TotalRevenue`
- No spaces (use underscores only if PascalCase is not supported)
- Avoid abbreviations: `CustomerIdentifier` not `CustID`
- Boolean columns: prefix with `Is` or `Has`: `IsActive`, `HasDiscount`
- Key columns: suffix with `Key`: `CustomerKey`, `ProductKey`

### 8.3 Measure Naming Standards

- Use descriptive names with aggregation context: `[Total Revenue]`, `[Average Order Value]`
- Time-intelligence measures: include period suffix: `[Revenue YTD]`, `[Revenue LY]`, `[Revenue MoM%]`
- KPI targets: prefix with `Target`: `[Target Revenue]`, `[Target Units]`

---

## 9. Power BI Optimization

### 9.1 VertiPaq Compression Principles

- Integer columns compress far better than string columns
- Low cardinality columns compress better than high cardinality
- Remove unused columns before import — every column consumes memory
- Sort columns by cardinality for maximum compression efficiency

### 9.2 DirectQuery Considerations

| Factor | Import Mode | DirectQuery Mode |
|---|---|---|
| Data freshness | Refresh-dependent | Real-time |
| Performance | Fast (in-memory) | Dependent on source |
| Dataset size limit | 10 GB (Pro) / 400 GB (Premium) | Unlimited |
| DAX support | Full | Partial |

### 9.3 Composite Models

Composite models mix Import and DirectQuery tables in a single semantic model.

**When to use:**
- Large fact tables in DirectQuery, small dimension tables in Import
- Real-time operational data alongside historical aggregates

**Governance requirement:** Composite model usage must be documented in the dataset's governance certificate. Data Detective flags undocumented composite models as Info severity.

### 9.4 Incremental Refresh

Incremental refresh partitions large fact tables so that only new data is refreshed, while historical partitions remain intact.

**Requirements for incremental refresh:**
- Two parameters defined in Power Query: `RangeStart` and `RangeEnd`
- Filter applied to the date column in the source query
- Detect data changes option configured for efficiency

---

## 10. Model Health Checklist

### Pre-Deployment Model Health Assessment

**Schema Structure:**
- [ ] Star schema confirmed (no unresolved snowflake sub-dimensions)
- [ ] All fact tables have defined and documented grain
- [ ] All dimension tables have integer surrogate keys
- [ ] Date dimension present and fully covers fact table date ranges

**Relationships:**
- [ ] All relationships are 1:M from dimension to fact
- [ ] No unexplained M:M relationships
- [ ] Cross-filter direction is Single unless documented exception
- [ ] Role-playing dimensions are implemented as calculated table copies

**Measures:**
- [ ] All measures in dedicated measure tables
- [ ] All measures have format strings defined
- [ ] No measure logic duplicated as calculated columns
- [ ] Non-additive measures use explicit DAX aggregation

**Naming:**
- [ ] Table names follow Dim/Fact/Bridge prefix convention
- [ ] Column names are in PascalCase without spaces
- [ ] Boolean columns prefixed with Is/Has
- [ ] Measure names include aggregation type and period where relevant

**Performance:**
- [ ] Unused columns removed from import
- [ ] String keys replaced with integer surrogate keys
- [ ] High-cardinality text columns reviewed for necessity
- [ ] Incremental refresh configured for fact tables > 1M rows

---

## 11. Practical Scenarios

### Scenario 1 — Mixed Grain Fact Table
**Dataset:** Monthly sales extract from ERP system  
**Problem:** Rows alternate between order-header totals and line-item details, producing duplicate revenue when summed  
**Analysis:** `SUM([Revenue])` returns 180% of actual revenue due to double-counting header and line amounts  
**Recommendation:** Enforce a single grain at the line-item level; remove header-level rows or create a separate aggregated fact table  
**Business Impact:** Executive dashboard overstates revenue by $4.2M — strategic pricing decisions distorted

### Scenario 2 — String-Based Relationship Keys
**Dataset:** Customer dimension joined to fact via `CustomerCode = "AU-CUST-00423"`  
**Problem:** VertiPaq stores string keys inefficiently; relationship resolution is slow  
**Analysis:** Report page with 12 visuals takes 14 seconds to render; equivalent model with integer keys renders in 1.8 seconds  
**Recommendation:** Add integer surrogate key in the ETL layer; preserve natural key as reference-only column  
**Business Impact:** User adoption of self-service BI drops 40% due to perceived slowness

### Scenario 3 — Missing Date Dimension
**Dataset:** E-commerce transaction data with `OrderDate` column in fact table  
**Problem:** Power BI Auto Date/Time enabled, generating hidden date hierarchies per date column, inflating model size by 600 MB  
**Analysis:** Model has 7 date columns, each generating its own hidden hierarchy — 7 × 87 MB overhead  
**Recommendation:** Disable Auto Date/Time globally; create one shared `DimDate` table; mark as date table  
**Business Impact:** Report load time reduced from 11s to 2.3s; model memory footprint reduced 65%

### Scenario 4 — Bidirectional Relationships Everywhere
**Dataset:** Retail analytics model with 11 bidirectional cross-filter relationships  
**Problem:** Filter context ambiguity causes circular dependency warnings; some measures return incorrect totals  
**Analysis:** DAX Studio shows 3 measures invoking disambiguation, each adding 400–700ms overhead  
**Recommendation:** Revert all relationships to single-direction; use `CROSSFILTER()` in specific measures where bidirectional filtering is required  
**Business Impact:** Dashboard KPIs showing inventory counts inflated by 12% due to unchecked filter propagation

### Scenario 5 — Calculated Columns for Aggregations
**Dataset:** Financial reporting model; analysts created 34 calculated columns for running totals  
**Problem:** Each calculated column is stored in VertiPaq; 34 columns add 2.1 GB to model size  
**Analysis:** Running total columns cannot respond to slicer context — they always show full dataset totals regardless of filters  
**Recommendation:** Remove all aggregation-based calculated columns; replace with DAX measures using `CALCULATE` and `FILTER`  
**Business Impact:** Budget vs. actuals reports filter correctly after measure conversion; model size reduced from 3.8 GB to 1.7 GB

### Scenario 6 — Snowflake Sub-Dimensions in Production
**Dataset:** Product hierarchy maintained as 4-level snowflake: Product → SubCategory → Category → Division  
**Problem:** Every product-related query requires 3 relationship hops, each adding filter evaluation overhead  
**Analysis:** Page render time for product hierarchy visuals averages 8.2 seconds; VertiPaq cache miss rate elevated  
**Recommendation:** Flatten to a single `DimProduct` table with `SubCategoryName`, `CategoryName`, `DivisionName` columns  
**Business Impact:** Product performance dashboard render time drops to 1.1 seconds; analyst productivity improves measurably

### Scenario 7 — No Fiscal Calendar in Date Dimension
**Dataset:** Financial controller's revenue dataset; company operates on April–March fiscal year  
**Problem:** YTD calculations based on calendar year misalign with company reporting; Q1 in the dashboard is January–March instead of April–June  
**Analysis:** Finance team reconciled manually every quarter, spending 12 hours per cycle correcting report outputs  
**Recommendation:** Add `FiscalYear`, `FiscalQuarter`, `FiscalMonth`, `FiscalWeek` to `DimDate`; rewrite all YTD and QTD measures using fiscal date columns  
**Business Impact:** Quarterly board report data integrity restored; 12 hours manual reconciliation eliminated per cycle

### Scenario 8 — M:M Relationship from Missing Bridge Table
**Dataset:** HR workforce analytics; employees assigned to multiple projects  
**Problem:** Direct M:M relationship between `DimEmployee` and `DimProject` causes headcount double-counting  
**Analysis:** Headcount KPI reports 1,840 employees when actual headcount is 1,200 — 53% inflation  
**Recommendation:** Create `BridgeEmployeeProject` with `EmployeeKey`, `ProjectKey`, `AllocationPercent`, `StartDate`, `EndDate`  
**Business Impact:** Executive workforce capacity reports corrected; prior 6 months of inflated headcount data flagged for re-issuance

### Scenario 9 — Measures Without Format Strings
**Dataset:** Executive KPI dashboard with 47 measures; none have format strings defined  
**Problem:** Revenue displays as `1823442.73` instead of `$1,823,443`; percentages display as `0.342` instead of `34.2%`  
**Analysis:** Executive users requested manual formatting on every visual — 47 visuals × 3 reports = 141 individual format overrides  
**Recommendation:** Apply format strings at the measure level: `"$#,##0"` for currency, `"0.0%"` for percentages, `"#,##0"` for whole numbers  
**Business Impact:** Report maintenance burden reduced; formatting consistency enforced across all consumers of the semantic model

### Scenario 10 — Fact Table with No Defined Grain
**Dataset:** Supply chain inventory snapshot; fact table contains both daily snapshots and weekly aggregates mixed  
**Problem:** Inventory on-hand measure over-counts because daily and weekly rows both exist for the same week  
**Analysis:** `SUM([InventoryUnits])` for a single SKU returns 3× the actual inventory value in weekly reports  
**Recommendation:** Separate into two fact tables: `FactInventoryDaily` (grain = SKU per day) and `FactInventoryWeekly` (grain = SKU per week)  
**Business Impact:** Procurement decisions based on 3× inflated inventory values caused $780K in unnecessary stock purchases

### Scenario 11 — Inactive Relationships Not Utilized
**Dataset:** Logistics model with `OrderDate`, `DispatchDate`, `DeliveryDate` — all pointing to one active `DimDate` table  
**Problem:** Only `OrderDate` relationship is active; `DispatchDate` and `DeliveryDate` have no inactive relationships defined  
**Analysis:** Delivery performance and dispatch lag measures cannot be computed — analysts use workarounds adding 3 hours per report cycle  
**Recommendation:** Create `DimDate_Dispatch` and `DimDate_Delivery` as calculated table copies; establish inactive relationships; implement `USERELATIONSHIP()` in relevant measures  
**Business Impact:** Logistics KPI accuracy restored; on-time delivery metric now correctly computed against actual delivery date

### Scenario 12 — Auto Date/Time Enabled on DirectQuery Model
**Dataset:** DirectQuery model connecting to Azure Synapse; Auto Date/Time enabled by default  
**Problem:** Power BI attempts to generate date hierarchies in-memory for a DirectQuery table — unsupported behavior causing errors  
**Analysis:** Report users see `CALENDAR` function error on date slicers; 6 of 14 visuals fail to render  
**Recommendation:** Disable Auto Date/Time; create a DimDate table in Synapse; import it (Import mode) as part of a composite model  
**Business Impact:** Report failure rate drops from 43% to 0%; executive dashboard certified for production deployment

### Scenario 13 — Duplicate Measure Logic Across Reports
**Dataset:** Three separate Power BI files all define `[Total Revenue]` differently  
**Problem:** Report A: `SUM([NetAmount])`; Report B: `SUM([GrossAmount])`; Report C: `SUM([InvoiceAmount])` — all labeled "Total Revenue"  
**Analysis:** Executive comparing three reports sees revenue figures that differ by $2.1M to $4.7M depending on report source  
**Recommendation:** Certify a single enterprise semantic model; define `[Total Revenue]` once using agreed business definition; deprecate individual report-level datasets  
**Business Impact:** Executive trust in BI reporting restored; single source of truth established for revenue metric

### Scenario 14 — High Cardinality Text Column in Fact Table
**Dataset:** Customer transaction log with `TransactionDescription` free-text column (900,000 unique values) stored in fact table  
**Problem:** VertiPaq cannot compress the column effectively; it consumes 1.4 GB of the 2.1 GB total model size  
**Analysis:** Column is used in 0 of 34 report visuals — it was imported by accident from the source extract  
**Recommendation:** Remove `TransactionDescription` from the Power Query query; store in operational database only if needed for drill-through  
**Business Impact:** Model size reduced 67%; refresh time reduced from 48 minutes to 11 minutes

### Scenario 15 — No Measure Table Organization
**Dataset:** Enterprise HR model with 112 measures scattered across 8 tables  
**Problem:** Analysts cannot locate relevant measures; duplicate measures created independently by different teams  
**Analysis:** 14 duplicate measures found with identical logic but different names; 23 measures flagged as potentially obsolete  
**Recommendation:** Consolidate all measures into domain-specific measure tables: `_RevenueMeasures`, `_HRMeasures`, `_LogisticsMeasures`; hide all measure tables from report view except measure display names  
**Business Impact:** New analyst onboarding time reduced from 3 weeks to 4 days; duplicate logic eliminated from governance backlog

### Scenario 16 — Relationships Based on Text Columns
**Dataset:** Order fact table joined to customer dimension via `CustomerName` (text)  
**Problem:** "Acme Corporation" and "ACME Corporation" treated as two different customers — 340 relationship breaks identified  
**Analysis:** 3.4% of fact rows have no matching dimension row; these are silently excluded from all measures  
**Recommendation:** Introduce `CustomerKey` (integer surrogate) as the join column; resolve name inconsistencies in the dimension table  
**Business Impact:** 3.4% of order revenue ($1.2M annual) was invisible in executive dashboards

### Scenario 17 — Incremental Refresh Not Configured on 50M Row Fact
**Dataset:** Telecommunications CDR (call data records) fact table, 50M rows, refreshed daily  
**Problem:** Full refresh runs 4.5 hours daily; dataset frequently times out in Power BI service (Premium timeout = 5 hours)  
**Analysis:** Only 50,000 new rows added per day; 99.9% of data is static historical data refreshed unnecessarily  
**Recommendation:** Configure incremental refresh: 3-year historical archive, 3-day refresh window, detect data changes enabled  
**Business Impact:** Daily refresh time reduced to 4 minutes; Power BI Premium capacity freed for other workloads

### Scenario 18 — Boolean Columns Stored as Text
**Dataset:** Customer dimension with `IsActive` column stored as `"Y"` / `"N"` text values  
**Problem:** Cannot use column in DAX conditional logic without text comparison; VertiPaq stores 2-value text column less efficiently than True/False Boolean  
**Analysis:** 14 Boolean-equivalent text columns identified across 6 dimension tables  
**Recommendation:** Convert to `TRUE`/`FALSE` Boolean in Power Query using `= [IsActive] = "Y"` transformation  
**Business Impact:** DAX measure logic simplified; model performance marginally improved; Boolean filter visuals work correctly

### Scenario 19 — SCD Type 2 Dimension Without IsCurrent Filter
**Dataset:** Product pricing history stored as SCD Type 2 with `ValidFrom` and `ValidTo` columns  
**Problem:** No `IsCurrent` flag; every product has 3–7 historical rows; fact-to-dimension join returns multiple matches  
**Analysis:** Revenue measure inflated 4× for some products due to fan-out from multiple matching dimension rows  
**Recommendation:** Add `IsCurrent = (ValidTo IS NULL OR ValidTo > TODAY())` column; apply default filter in relationships or use a current-state snapshot dimension separately  
**Business Impact:** Product revenue reporting corrected; prior financial reports flagged for audit review

### Scenario 20 — Model Deployed Without Documentation
**Dataset:** 87-measure enterprise sales model deployed to production Power BI workspace  
**Problem:** No measure descriptions, no table documentation, no data lineage, no refresh schedule documentation  
**Analysis:** When original developer left, no one could modify or certify the model; 3 governance audits blocked  
**Recommendation:** Require documentation as a deployment gate: measure descriptions via `SETDESC()`, table descriptions in tabular model annotations, external data dictionary linked in workspace metadata  
**Business Impact:** Model locked for 4 months pending governance remediation; 14 dependent reports suspended

---

## 12. Semantic Model Design Summary

| Design Decision | Recommended | Not Recommended |
|---|---|---|
| Schema type | Star schema | Snowflake without flattening |
| Key type | Integer surrogate | String natural key |
| Measures | In measure tables | Scattered across data tables |
| Date dimension | Dedicated DimDate | Auto Date/Time |
| Relationships | 1:M, single direction | M:M, bidirectional by default |
| Grain definition | Explicitly documented | Implicit or mixed |
| Calculated columns | Row-level attributes only | Aggregations and running totals |

---

*This document is part of the Data Detective Governance Knowledge Base. Version 1.0. For use as RAG retrieval context in Microsoft Foundry IQ.*
