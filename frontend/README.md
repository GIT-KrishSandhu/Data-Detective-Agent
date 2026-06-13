# Frontend – Data Detective Agent

## Overview

The frontend is built with **Next.js + React + TypeScript** and serves as the visual interface for the **Data Detective Reasoning Agent**. Rather than functioning as a traditional chatbot, the UI visualizes the execution of a deterministic multi-agent reasoning pipeline for Business Intelligence and data quality assessment.

## Key Features

* Dataset Ingestion Explorer
* Multi-Agent Orchestration Pipeline
* Live Runtime Status Panel
* Semantic Blackboard Visualization
* Agent Telemetry Streams
* Power BI Readiness Dashboard
* Data Quality Audit Reports
* Executive Certificate Generation
* Microsoft Foundry IQ Grounding Indicators

## Architecture

```
CSV Upload
     │
     ▼
Frontend UI
     │
     ▼
FastAPI Backend
     │
     ▼
Planner Agent
     │
     ▼
Specialized Reasoning Agents
     │
     ▼
Semantic Blackboard
     │
     ▼
Microsoft Foundry IQ Grounding
     │
     ▼
Azure AI Foundry (gpt-5-mini)
```

## Technology Stack

* Next.js
* React
* TypeScript
* Tailwind CSS
* Lucide React Icons

## Runtime Panels

The interface exposes the complete reasoning process instead of only displaying final AI outputs.

Displayed runtime information includes:

* Azure AI Foundry Provider
* GPT-5-mini Language Layer
* Semantic Blackboard Reasoning Engine
* Microsoft Foundry IQ Knowledge Grounding
* Retrieved Enterprise Context
* Deterministic Execution Status

## Design Philosophy

The interface is designed around **explainable AI**.

Instead of hiding analysis behind a single LLM response, every reasoning stage is visible:

* Planner Agent
* Quality Agent
* BI Readiness Agent
* Evaluation Agent

Each agent publishes validated findings to a shared Semantic Blackboard before executive language synthesis occurs.

## Local Development

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

The application will be available at:

```
http://localhost:3000
```

Ensure the backend API is running and the required environment variables are configured.

## Project Goal

Data Detective demonstrates a **Reasoning Agent architecture** where deterministic Python analytics produce validated evidence, Microsoft Foundry IQ supplies enterprise grounding, and Azure AI Foundry GPT-5-mini communicates those findings in clear business language.

The frontend is intentionally designed to make every reasoning step transparent, explainable, and auditable.
