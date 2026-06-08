# Data Detective Agent

Data Detective Agent is an evidence-first, multi-agent data readiness platform built for the **Microsoft Agents League Hackathon**. 

It enables teams, analysts, and developers to upload large datasets, automatically profile schemas, audit data quality, construct clean star schemas, and compile stakeholder summaries—all with strict data safety constraints, comprehensive telemetry tracking, and zero hallucinated insights.

---

## 🚀 Key Features

* **Data Quality Audit**: Automatic schema parsing and constraint validation (missing columns, type mismatches, anomalies).
* **Exploratory Data Analysis (EDA)**: Profiling distributions, standard metrics (mean, median, std dev), and correlations.
* **Executive Summary**: Evidence-first insights compiled into executive summaries for business users.
* **Power BI Preparation**: Suggesting denormalization plans, clean schemas, and clean table headers to streamline Power BI imports.
* **Evidence-First Principle**: Every report statement and visualization is linked directly to a traceable SQL or Pandas query. No forecasting, no predictions, and no unsupported claims.
* **Human-in-the-Loop Safeguards**: Data cleaning policies are previewed in code format. No modifications are applied to the dataset without explicit human approval.

---

## 🛠️ Technology Stack

* **Frontend**: Next.js 15+ (App Router), TypeScript, Tailwind CSS, shadcn/ui, Plotly.js
* **Backend**: FastAPI, Python 3.12, Uvicorn
* **Agent Layer**: LangGraph, LangChain (Provider-Agnostic LLM integration)
* **Database**: PostgreSQL (using async SQLAlchemy with asyncpg)
* **Deployment Target**: Local development (first phase), Azure App Services & Azure Database for PostgreSQL (later phase)

---

## 📂 Project Structure

```
Data-Detective-Agent/
│
├── frontend/                     # Next.js 15+ App Router Web Application
│   ├── app/                      # App layouts and pages (page.tsx, layout.tsx)
│   ├── components/               # Reusable UI component blocks (shadcn/ui buttons, cards)
│   ├── lib/                      # Helper modules and styling utilities
│   ├── hooks/                    # Custom React hooks
│   ├── types/                    # TypeScript interfaces
│   └── services/                 # API connection modules
│
├── backend/                      # Python 3.12 FastAPI Server
│   ├── api/                      # Routing routes and endpoints (v1 registry)
│   ├── agents/                   # Agent core modules
│   │   ├── planner/              # Drafts the analysis path based on goals
│   │   ├── quality/              # Inspects schemas for missing fields and type errors
│   │   ├── statistics/           # Profiles distributions and correlation matrices
│   │   ├── visualization/        # Formulates Plotly spec queries for client rendering
│   │   ├── cleaning/             # Generates cleaning policy recommendations
│   │   ├── critic/               # Verification guardrail (prevents forecasting & hallucinations)
│   │   ├── evaluation/           # Validates calculations and links statements to queries
│   │   └── report/               # Compiles final report markdown and outputs
│   │
│   ├── tools/                    # Tool interfaces (Inspect, profile, edit)
│   ├── services/                 # Common services (telemetry logging)
│   ├── database/                 # SQLAlchemy connections and sessions
│   ├── models/                   # DB schema model structures
│   ├── schemas/                  # Pydantic query schemas
│   ├── prompts/                  # Large Language Model instructions
│   └── core/                     # Server settings and environmental configurations
│
├── docs/                         # Architecture, responsibilities, and workflow guides
│
├── .env.example                  # Template configuration for backend keys
└── README.md                     # Platform guide and quickstart
```

---

## ⚙️ Quick Start Guide

### Prerequisites
- [Node.js v20+](https://nodejs.org/)
- [Python v3.12+](https://www.python.org/)
- [PostgreSQL v15+](https://www.postgresql.org/) (Running locally)

---

### Backend Setup

1. **Navigate to the backend directory and create a virtual environment**:
   ```bash
   cd backend
   python -m venv .venv
   ```

2. **Activate the virtual environment**:
   - **Windows PowerShell**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     source .venv/bin/activate
     ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**:
   Copy `.env.example` to the root directory as `.env` and fill in your details:
   ```bash
   cp ../.env.example ../.env
   ```

5. **Start the FastAPI Dev Server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   *The Swagger interactive documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

---

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install node dependencies**:
   ```bash
   npm install
   ```

3. **Run the Next.js development server**:
   ```bash
   npm run dev
   ```
   *Open [http://localhost:3000](http://localhost:3000) to view the client dashboard.*

---

## 🛡️ Core Agent Safety Guidelines
This project enforces rigid safety principles defined in [architecture.md](file:///c:/Users/krish/Desktop/AI%20Skills%20Fest/Data-Detective-Agent/docs/architecture.md):
1. **Descriptive Only**: Agents must not attempt time-series forecasting, predictive modeling, or extrapolation.
2. **Hard Database Evidence**: No insight is permitted in the final report unless it is accompanied by an audit trail (SQL check or Pandas aggregate script) verified by the `EvaluationAgent`.
3. **No Automatic Edits**: Under no circumstances can data cleaning scripts be applied to the primary dataset without human review and button-confirmation via the UI.