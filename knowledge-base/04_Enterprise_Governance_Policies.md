# 04 — Enterprise Data Governance Policies
## Power BI Dataset Governance Reference for Data Detective

---

## Executive Summary

Data governance is the organizational framework that ensures data assets are formally owned, adequately documented, consistently maintained, and appropriately secured throughout their lifecycle. Without governance, Power BI datasets become ungoverned artifacts that drift in quality, accumulate technical debt, and eventually produce misleading business intelligence. This document defines the enterprise governance policies that Data Detective enforces as pre-deployment quality gates, audit criteria, and certification prerequisites. These policies are intended for retrieval by Microsoft Foundry IQ to generate governance certificate content, management recommendations, and executive signoff documentation.

---

## 1. Data Ownership

### 1.1 Definition

A **Data Owner** is the named executive or senior manager who bears ultimate accountability for a dataset's accuracy, fitness for purpose, and compliance with organizational policies.

### 1.2 Data Owner Responsibilities

| Responsibility | Description |
|---|---|
| Accuracy accountability | Accountable for the dataset correctly representing business reality |
| Approval authority | Must approve dataset for production deployment |
| Incident response | Receives critical quality incident notifications |
| Policy compliance | Ensures dataset meets all governance requirements |
| Lifecycle decisions | Approves dataset retirement, archival, or replacement |

### 1.3 Data Owner Assignment Requirements

- Every dataset in a governed Power BI workspace **must** have a named Data Owner
- Data Owner must be a permanent employee (not contractor) with authority in the business domain
- Data Owner must be assigned **before** a dataset is submitted for BI Readiness assessment
- Data Owner identity must be recorded in the dataset's governance metadata field

**Governance Flag:** Any dataset submitted to Data Detective without a named Data Owner will receive a Critical governance flag and cannot proceed to certification.

---

## 2. Data Stewardship

### 2.1 Definition

A **Data Steward** is the operational subject matter expert responsible for the day-to-day quality management, documentation, and issue resolution for a dataset.

### 2.2 Data Steward Responsibilities

| Responsibility | Description |
|---|---|
| Quality monitoring | Reviews quality reports and accepts/escalates issues |
| Issue remediation | Coordinates resolution of Warning-level quality issues |
| Documentation | Maintains data dictionary and business definitions |
| Change management | Reviews and approves schema changes |
| Lineage maintenance | Keeps data lineage diagrams current |
| User support | First point of contact for dataset consumers |

### 2.3 Steward vs. Owner Distinction

| Criterion | Data Owner | Data Steward |
|---|---|---|
| Level | Executive / Senior Manager | Analyst / Subject Matter Expert |
| Accountability | Strategic and regulatory | Operational and quality |
| Meeting frequency | Quarterly governance review | Weekly data quality review |
| Approval scope | Production deployment, retirement | Schema changes, quality acceptance |

---

## 3. Dataset Lifecycle Management

### 3.1 Dataset Lifecycle Stages

```
[Draft] → [Development] → [Testing] → [Production] → [Deprecated] → [Retired]
```

**Stage Definitions:**

| Stage | Description | Access | Governance Required |
|---|---|---|---|
| Draft | Under initial development; schema unstable | Data Engineer only | Ownership assignment |
| Development | Being built; schema defined; not tested | Engineering team | Ownership + Stewardship |
| Testing | UAT in progress; business validation underway | Engineering + Business Analysts | Full governance + quality audit |
| Production | Certified and deployed; active use | All authorized users | Full certification maintained |
| Deprecated | Superseded by newer version; read-only | Existing users only | Deprecation notice issued |
| Retired | Decommissioned; archived or deleted | Archive access only | Retirement record maintained |

### 3.2 Lifecycle Transition Requirements

**Draft → Development:**
- [ ] Data Owner assigned
- [ ] Data Steward assigned
- [ ] Schema documented in governance register

**Development → Testing:**
- [ ] Data Detective quality audit passed (no Critical issues)
- [ ] BI Readiness Score ≥ 65
- [ ] Data lineage documented

**Testing → Production:**
- [ ] BI Readiness Score ≥ 80
- [ ] UAT sign-off from Business Analyst
- [ ] Data Owner production approval
- [ ] Security review completed
- [ ] Governance certificate issued

**Production → Deprecated:**
- [ ] Successor dataset identified and certified
- [ ] Deprecation notice issued to all consumers (minimum 30 days notice)
- [ ] Data Owner approves deprecation
- [ ] Migration guide published

**Deprecated → Retired:**
- [ ] Retirement date communicated to all consumers
- [ ] Archive or deletion decision documented
- [ ] Data Owner approves retirement
- [ ] Audit trail preserved for minimum 7 years (where applicable)

---

## 4. Production Approval Process

### 4.1 Production Approval Gate Requirements

Before any dataset is promoted to a production Power BI workspace, the following approvals must be obtained and documented:

| Gate | Approver | Evidence Required |
|---|---|---|
| Quality Gate | Data Steward | Signed quality acceptance form |
| Technical Gate | Lead Data Engineer | BI Readiness Score ≥ 80 |
| Security Gate | Information Security Team | Security review sign-off |
| Business Gate | Data Owner | Business validation confirmation |
| Governance Gate | Data Governance Committee | Governance certificate number |

### 4.2 Expedited Approval Process

In exceptional circumstances, expedited approval may be requested for urgent business needs. Expedited approval requires:
- Documented business justification signed by a C-level executive
- Acceptance of all outstanding Warning issues by Data Owner
- Post-deployment remediation plan with 30-day resolution commitment
- Monitoring plan for the period until full remediation

**Policy:** Expedited approval cannot override Critical-severity quality issues. Critical issues must be resolved before any production deployment regardless of urgency.

---

## 5. Audit Requirements

### 5.1 Dataset Audit Frequency

| Dataset Classification | Audit Frequency | Trigger Events |
|---|---|---|
| Executive / Board reporting | Monthly | Schema change, source change, quality alert |
| Operational reporting | Quarterly | Schema change, quality alert |
| Analytical / Exploratory | Bi-annually | Source change |
| Archived | Not audited | Retirement review only |

### 5.2 Audit Scope

A dataset audit conducted by Data Detective must include:

**Quality Audit:**
- [ ] Completeness profile for all columns
- [ ] Uniqueness check for all key columns
- [ ] Business rule validation against registered rule set
- [ ] Outlier detection on all measure columns
- [ ] Referential integrity check for all relationships
- [ ] Date format and range validation

**Schema Audit:**
- [ ] Schema comparison against last certified version
- [ ] New column identification and classification
- [ ] Removed column impact assessment
- [ ] Data type change detection

**Governance Audit:**
- [ ] Data Owner still in role (employment status check)
- [ ] Data Steward still assigned
- [ ] Data dictionary currency (≥ 80% of columns described)
- [ ] Lineage diagram current
- [ ] Sensitivity classification confirmed

### 5.3 Audit Trail Requirements

All audit results must be stored with the following metadata:
- Audit ID (unique, auto-generated)
- Dataset Name and Version
- Audit Date and Time (UTC)
- Audited By (Data Detective agent version)
- Issues Detected (count by severity)
- Readiness Score at Audit Time
- Certifier (Data Steward name)
- Next Audit Due Date

**Retention Policy:** Audit records must be retained for a minimum of 7 years for datasets used in financial, regulatory, or compliance reporting.

---

## 6. Version Control

### 6.1 Dataset Versioning Standard

All governed datasets must implement semantic versioning:

```
MAJOR.MINOR.PATCH
  MAJOR: Breaking schema change (column removed, type changed, grain changed)
  MINOR: Non-breaking schema change (column added, description updated)
  PATCH: Data correction (quality fix, backfill, deduplication)
```

**Examples:**

| Change | Version Increment | Notification Required |
|---|---|---|
| New column added to DimProduct | 1.0.0 → 1.1.0 | Info notification to consumers |
| Revenue column renamed | 1.1.0 → 2.0.0 | Breaking change notice; 30-day migration period |
| Duplicate records removed | 1.1.0 → 1.1.1 | Info notification; restate prior period if material |
| Date grain changed from monthly to daily | 1.1.1 → 2.0.0 | Breaking change; full re-certification required |

### 6.2 Version Control Requirements

- All schema changes must be recorded in a change log
- Breaking changes (MAJOR version) require full re-certification
- All versions must be stored in the source version control system (e.g., Azure DevOps)
- Power BI semantic model PBIX files must be version-controlled alongside source datasets

---

## 7. Data Lineage

### 7.1 Lineage Documentation Requirements

Data lineage documents the complete journey of data from source system to Power BI visual.

**Required lineage elements:**

| Element | Description |
|---|---|
| Source System | Name, type, and owner of the originating system |
| Extraction Method | API, database query, file export, stream |
| Transformation Steps | Each ETL/ELT transformation applied |
| Loading Target | Data warehouse, lakehouse, or direct connection |
| Power BI Dataset | Dataset name and workspace |
| Power BI Reports | All reports consuming the dataset |
| Downstream Alerts | Dashboards, alerts, and subscriptions |

### 7.2 Lineage Format Standard

Lineage must be documented in one of the following formats:
- Microsoft Purview automated lineage (preferred for Azure-native pipelines)
- Data Detective lineage metadata JSON (auto-generated during audit)
- Approved lineage diagram in the governance documentation repository

**Governance Flag:** Any dataset lacking documented lineage will receive a Warning governance flag. Datasets used in regulatory or financial reporting that lack lineage will receive a Critical governance flag.

---

## 8. Access Control

### 8.1 Power BI Workspace Access Levels

| Role | Access | Appropriate For |
|---|---|---|
| Admin | Full control including deletion | BI Team Lead only |
| Member | Publish and modify content | BI Developer |
| Contributor | Publish content; cannot configure workspace | Senior Analyst |
| Viewer | Read reports and dashboards only | Business Users |

### 8.2 Row-Level Security Requirements

Row-Level Security (RLS) is mandatory for datasets containing:
- Personally Identifiable Information (PII)
- Payroll or compensation data
- Individual employee performance data
- Customer-specific financial data
- Commercially sensitive information

**RLS Implementation Standards:**
- Use dynamic RLS wherever possible (`USERNAME()` and `USERPRINCIPALNAME()` functions)
- Static RLS roles must be documented and reviewed quarterly
- RLS roles must be tested by the Security team before production deployment
- RLS must be validated after every MAJOR version update

### 8.3 Sensitivity Classification

All datasets must be assigned one of the following sensitivity labels:

| Classification | Description | Access Controls Required |
|---|---|---|
| Public | Non-sensitive aggregated data | Workspace viewer access |
| Internal | Business data; no regulatory concern | Authenticated employees |
| Confidential | Commercially sensitive; strategic data | Named user groups; RLS required |
| Restricted | PII, financial, regulatory, HR data | RLS mandatory; audit logging required |
| Highly Restricted | Board-level, M&A, regulatory | Executive-only; additional authentication |

---

## 9. Documentation Requirements

### 9.1 Required Documentation per Dataset

| Document | Description | Owner | Review Frequency |
|---|---|---|---|
| Data Dictionary | All columns with business definitions | Data Steward | With each MINOR version |
| Business Rules Register | All validation rules applied | Data Steward | Quarterly |
| Lineage Diagram | Source-to-visual data flow | Data Engineer | With each MAJOR version |
| Quality Report | Latest Data Detective audit results | Data Detective (automated) | Each refresh cycle |
| Governance Certificate | Certification status and conditions | Data Governance Committee | At certification and renewal |
| Refresh Schedule | Expected refresh frequency and timing | Data Engineer | When schedule changes |
| Known Issues Register | Outstanding quality issues and acceptance rationale | Data Steward | Ongoing |

### 9.2 Documentation Quality Standards

- Documentation must be in plain business English
- No technical jargon in column descriptions intended for business users
- All business rules must include at least one pass and one fail example
- Data dictionary entries must include: column name, data type, business definition, allowed values or range, and example values

---

## 10. Quality Gates for Deployment

### 10.1 Quality Gate Definition

A **Quality Gate** is a mandatory checkpoint that a dataset must pass before it can transition to the next lifecycle stage. Quality Gates are automated by Data Detective and cannot be manually overridden without documented executive escalation.

### 10.2 Quality Gate Registry

| Gate ID | Gate Name | Stage Transition | Automatable | Override Authority |
|---|---|---|---|---|
| QG-01 | Primary Key Integrity | Development → Testing | Yes | None — no override |
| QG-02 | Foreign Key Completeness | Development → Testing | Yes | None — no override |
| QG-03 | Business Rule Validation | Development → Testing | Yes | Data Owner + CDAO |
| QG-04 | BI Readiness Score ≥ 65 | Development → Testing | Yes | Data Owner |
| QG-05 | BI Readiness Score ≥ 80 | Testing → Production | Yes | Data Owner + CDAO |
| QG-06 | Governance Certificate Issued | Testing → Production | Partial | Data Governance Committee |
| QG-07 | Security Review Passed | Testing → Production | No | None — mandatory |
| QG-08 | Data Owner Sign-Off | Testing → Production | No | None — mandatory |

---

## 11. Monitoring and Continuous Governance

### 11.1 Production Monitoring Requirements

After deployment to production, datasets must be continuously monitored:

**Automated Monitoring (Data Detective or equivalent):**
- Daily: Row count delta (detect unexpected data drops)
- Daily: Null rate monitoring for key columns
- Weekly: Duplicate detection on primary keys
- Weekly: Business rule compliance rate
- Monthly: Full quality re-audit with readiness re-score

**Alert Thresholds:**

| Metric | Warning Threshold | Critical Threshold |
|---|---|---|
| Row count drop | > 10% drop from prior day | > 30% drop or 0 rows |
| Null rate increase | > 2% increase in mandatory columns | Any null in key columns |
| Refresh failure | 1 failure | 2 consecutive failures |
| Duplicate rate | > 0.1% | > 1% |
| Business rule violations | > 1% | > 5% |

### 11.2 Certification Renewal

Governance certificates are valid for 12 months. Renewal requires:
- A full Data Detective audit in the 30 days before expiry
- BI Readiness Score ≥ 80 maintained
- No unresolved Critical issues at renewal date
- Data Owner confirmation that dataset still serves its stated business purpose
- Data Steward confirmation that documentation is current

---

## 12. Executive Signoff Standards

### 12.1 When Executive Signoff is Required

| Scenario | Required Signoff Level |
|---|---|
| Initial production deployment | Data Owner (Director or above) |
| Deployment with accepted Warning issues | Data Owner + Data Governance Committee Chair |
| Expedited deployment bypass | C-level Executive + CDAO |
| Dataset retirement with active users | Data Owner + impacted department heads |
| Certification of board-level reporting dataset | CEO or CFO (domain-dependent) |

### 12.2 Executive Signoff Record Requirements

All executive signoffs must be:
- Digitally recorded (email confirmation or digital signature)
- Stored in the governance documentation repository
- Referenced by unique Governance Certificate number
- Retained for minimum 7 years

---

## 13. Governance Anti-Patterns

### 13.1 Common Governance Failures

| Anti-Pattern | Description | Consequence |
|---|---|---|
| Orphaned dataset | No data owner; developer who created it has left | No quality accountability; gradual drift to unusability |
| Shadow BI | Business team builds and publishes datasets without governance | Quality unknown; duplicates certified datasets; trust fragmented |
| Stale certification | Governance certificate expired; dataset still in use | Regulatory exposure; no accountability for quality changes |
| Override culture | Quality gates regularly overridden without escalation | Governance becomes performative; quality erodes |
| Undocumented RLS | Row-level security present but undocumented | Security review failures; potential data exposure |
| Version drift | Multiple versions of same dataset in production simultaneously | Consumer confusion; conflicting KPI values |
| Documentation debt | Data dictionary neglected; column descriptions never written | New analyst onboarding costs excessive; stewardship vacuum |

---

*This document is part of the Data Detective Governance Knowledge Base. Version 1.0. For use as RAG retrieval context in Microsoft Foundry IQ.*
