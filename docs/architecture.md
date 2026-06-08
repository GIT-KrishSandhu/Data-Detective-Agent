# Data Detective Agent - System Architecture

This document outlines the high-level architecture of the **Data Detective Agent** platform.

```mermaid
graph TD
    User([User App / Client]) -->|Upload Spreadsheet| API[FastAPI Backend]
    User -->|Select Goal & Launch| API
    
    subgraph Multi-Agent Graph Layer
        API -->|Instantiate Graph| LangGraph[LangGraph Workflow]
        
        LangGraph --> Planner[Planner Agent]
        Planner --> Quality[Quality Agent]
        Quality --> Statistics[Statistics Agent]
        Statistics --> Visualization[Visualization Agent]
        Visualization --> Cleaning[Cleaning Agent]
        
        Cleaning -->|Yield Actions| Approval{Human-in-the-Loop Approval}
        Approval -->|Confirmed| Critic[Critic Agent]
        
        Critic --> Evaluation[Evaluation Agent]
        Evaluation --> Report[Report Agent]
        
        Report -->|Final Report & Dataset| Out[Output Store]
    end
    
    subgraph Storage Layer
        API --> DB[(PostgreSQL Database)]
        Out --> DB
    end
```

## Architectural Design Patterns

### 1. Blackboard Architecture Pattern
All agents in the league write to and read from a shared, coordinate blackboard state (`AgentState`). This promotes loose coupling:
- Agents do not need to know the specific implementation details of other agents.
- Each agent performs its specialized operations and appends findings to the shared state.
- Intermediate results (e.g., statistical profiles) are stored transparently for other agents to read.

### 2. Provider-Agnostic LLM Binding
The `BaseAgent` class is designed to accept generic LangChain `BaseChatModel` interfaces. This makes the platform vendor-neutral, supporting local models (Ollama, Llama), standard endpoints (OpenAI GPT-4o), and cloud services (Azure OpenAI) via unified environment configurations.

### 3. Human-in-the-Loop (HITL) Gatekeeper
To ensure data safety, dataset modifications are never executed autonomously. The `CleaningAgent` outputs a list of proposed modifications with python preview statements. The graph execution yields control back to the user to confirm/reject these changes, saving the selections to the state before completing the remaining stages.

### 4. Telemetry and Logging
The system integrates structured logging at every step using `TelemetryLogger`. We track:
- Node entry and exit events.
- Response latencies.
- Token metrics per agent call.
- Database access and execution times for verification audits.
