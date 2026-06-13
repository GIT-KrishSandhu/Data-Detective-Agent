# Data Detective Agent

[![Microsoft Agents League Hackathon](https://img.shields.io/badge/Microsoft%20Hackathon-Agents%20League-blue.svg)](https://github.com/GIT-KrishSandhu/Data-Detective-Agent)
[![Reasoning Agent](https://img.shields.io/badge/Track-Reasoning%20Agent-purple.svg)]()
[![Azure AI Foundry](https://img.shields.io/badge/Azure%20AI-Foundry-blue.svg)]()
[![Microsoft Foundry IQ](https://img.shields.io/badge/Grounded%20With-Microsoft%20Foundry%20IQ-0078D4.svg)]()
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)]()
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)]()
[![Deterministic](https://img.shields.io/badge/Execution-Deterministic-16a34a.svg)]()

> **A multi-agent Reasoning System that deterministically audits datasets for Business Intelligence readiness, grounds enterprise recommendations with Microsoft Foundry IQ, and uses Azure AI Foundry GPT-5-mini exclusively for executive communication.**

---

# The Problem

Business dashboards are only as reliable as the datasets powering them.

Today's AI analytics assistants typically upload raw datasets directly into an LLM, forcing the model to perform statistical reasoning, schema validation, and business recommendations simultaneously.

This results in:

* hallucinated insights
* inconsistent recommendations
* poor reproducibility
* difficult enterprise auditing

---

# The Solution

Data Detective separates **reasoning** from **language generation**.

Instead of asking an LLM to analyze raw data, specialized deterministic agents execute Python and Pandas based validation tools, publish structured evidence to a shared Semantic Blackboard, retrieve enterprise best practices through Microsoft Foundry IQ, and finally invoke Azure AI Foundry GPT-5-mini to communicate validated findings in executive language.

---

# Architecture

```text
Dataset Upload
        │
        ▼
Planner Agent
        │
        ▼
Quality Agent
        │
        ▼
BI Readiness Agent
        │
        ▼
Evaluation Agent
        │
        ▼
Semantic Blackboard
        │
        ▼
Microsoft Foundry IQ
(Enterprise Knowledge Grounding)
        │
        ▼
Azure AI Foundry GPT-5-mini
(Executive Language Generation)
        │
        ▼
Business Intelligence Dashboard
```

---

# Core Features

## Deterministic Multi-Agent Reasoning

Every analytical conclusion is generated through deterministic Python execution.

Agents perform:

* Missing Value Analysis
* Duplicate Detection
* Mixed Type Detection
* Identifier Discovery
* High Cardinality Detection
* Distribution Profiling
* Outlier Analysis
* Schema Relationship Inspection
* Power BI Readiness Evaluation

No analytical decision is delegated to a language model.

---

## Semantic Blackboard Collaboration

Agents never communicate directly.

Instead they publish structured entities into a shared Semantic Blackboard where downstream agents consume validated evidence and contribute additional findings.

Benefits include:

* explainable reasoning
* reproducible execution
* versioned state transitions
* transparent agent collaboration

---

## Microsoft Foundry IQ Grounding

Data Detective incorporates Microsoft Foundry IQ as an enterprise grounding layer.

The knowledge corpus contains:

* Power BI Modeling Guide
* BI Readiness Framework
* Enterprise Governance Policies
* Data Quality Standards
* Semantic Model Best Practices
* Business Intelligence Case Studies

Relevant passages are retrieved before executive summaries are generated, ensuring recommendations remain grounded in enterprise documentation rather than unsupported language model inference.

---

## Azure AI Foundry Integration

Azure AI Foundry GPT-5-mini is responsible only for:

* Executive Summary
* Management Explanation
* Certificate Wording
* Markdown Export Generation

The model never computes analytical scores or validates datasets.

---

# Runtime Transparency

The application exposes its execution engine directly through the UI.

```
Provider:
Azure AI Foundry

Language Layer:
gpt-5-mini

Reasoning Engine:
Semantic Blackboard

Knowledge Grounding:
Microsoft Foundry IQ

Retrieved Context:
Enterprise Documents

Execution:
Deterministic
```

---

# Technology Stack

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* Shadcn/ui

## Backend

* FastAPI
* LangGraph
* Pandas
* PostgreSQL

## AI Services

* Azure AI Foundry GPT-5-mini
* Microsoft Foundry IQ
* Azure OpenAI

---

# Repository Structure

```
backend/
    agents/
    tools/
    services/
    api/

frontend/
    app/
    components/
    services/

docs/
    architecture.md
    workflow.md
    agent-responsibilities.md

foundry-grounding/
    Power BI guidance corpus
```

---

# Quick Start

## Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
```

Configure:

```
POSTGRES_SERVER=
POSTGRES_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5-mini
AZURE_OPENAI_API_VERSION=2025-04-01-preview
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Open:

```
http://localhost:3000
```

---

# Demo

1. Upload a CSV dataset
2. Observe Planner → Quality → BI Readiness → Evaluation execution
3. Watch live Telemetry Streams
4. Inspect Semantic Blackboard updates
5. View Microsoft Foundry IQ grounded runtime status
6. Review Data Quality Audit
7. Generate Enterprise Power BI Readiness Certificate

---

# Design Philosophy

> **Reason first. Retrieve enterprise knowledge second. Generate language last.**

Data Detective demonstrates how deterministic multi-agent reasoning, Semantic Blackboard collaboration, Microsoft Foundry IQ grounding, and Azure AI Foundry language synthesis can be combined to produce transparent, explainable, and enterprise-ready Business Intelligence insights.
