# GEMINI.md - HR Agentic Solution (MVP 1)

> **PRIMARY DIRECTIVE**: This repository strictly adheres to [PROJECT_CONFIG.md](file:///usr/local/google/home/inhyep/work/kr-elevate-module3/PROJECT_CONFIG.md) as the **single source of truth** for all project parameters, naming conventions, sub-agent contracts, and session state keys.

---

## 1. Unified Project & Infrastructure Parameters

All code, configurations, Terraform files, and environment loaders must use the following standard parameters:

| Parameter Key | Standard Value | Environment Variable / Config Key |
| :--- | :--- | :--- |
| **GCP Project ID** | `pe-kor-trainer` | `GOOGLE_CLOUD_PROJECT` |
| **GCP Project Number** | `775423734296` | `GOOGLE_CLOUD_PROJECT_NUMBER` |
| **GCP Region** | `global` | `GOOGLE_CLOUD_REGION` |
| **Default LLM Model** | `gemini-3.5-flash` | `MODEL_NAME` |
| **Vector Embedding Model** | `text-embedding-004` (768 dimensions) | `EMBEDDING_MODEL` |
| **Session Hydration Store** | Google Cloud Firestore / Redis | `FIRESTORE_DATABASE_ID` |
| **Audit Compliance Store** | Google Cloud Spanner | `SPANNER_INSTANCE_ID` |
| **Key Vaulting** | Google Secret Manager | `SECRET_MANAGER_PROJECT_ID` |

---

## 2. Unified Sub-Agent Contracts (Names & Descriptions)

When defining ADK `Agent` instances in `agent/sub_agents/` and `agent/root_orchestrator.py`, developers and AI agents must use the **exact** `name` and `description` strings specified below:

```python
# 1. Policy RAG Sub-Agent (Owner: Developer A)
policy_rag_agent = Agent(
    name="policy_rag_agent",
    model=MODEL_NAME,
    description="Answers employee questions about company HR policies (Leave, Remote Work, Expense, Relocation) with grounded citations.",
    ...
)

# 2. WorkWeek HCM Sub-Agent (Owner: Developer B)
workweek_agent = Agent(
    name="workweek_agent",
    model=MODEL_NAME,
    description="Handles WorkWeek HCM transactions: PTO balances, personal contact updates, and leave booking.",
    ...
)

# 3. ServiceImmediately ITSM Sub-Agent (Owner: Developer C)
itsm_agent = Agent(
    name="service_immediately_agent",
    model=MODEL_NAME,
    description="Handles ServiceImmediately ITSM operations: ticket status queries, incident creation, and comments.",
    ...
)

# 4. Root HR Orchestrator (Assembly)
hr_root_orchestrator = Agent(
    name="hr_root_orchestrator",
    model=MODEL_NAME,
    description="Main HR Orchestrator routing user intents and executing cross-system multi-step workflows.",
    sub_agents=[policy_rag_agent, workweek_agent, itsm_agent],
    ...
)
```

---

## 3. Backend Subsystem Protocols & Auth Headers

| Subsystem | Integration Protocol | Base Endpoint URL | Required Header / Secret Key |
| :--- | :--- | :--- | :--- |
| **WorkWeek (MCP)** | FastMCP Streamable HTTP | `/work-week/mcp/` | `X-MCP-Token: <ephemeral_token>` |
| **WorkWeek (REST)** | REST API | `/work-week/api/employees/{id}/` | `x-goog-authenticated-user-email` |
| **ServiceImmediately** | FastMCP Streamable HTTP | `/service-immediately/mcp/` | `X-MCP-Token: <ephemeral_token>` |
| **Policy Vector Store** | Local Vector Search | Local Embeddings | N/A |

---

## 4. Standard Session State Keys (`session.state`)

When reading or updating multi-turn session state across agents and tools, use the following standardized keys:

- `user_id`: Authenticated Employee ID (e.g. `"EMP-1004"`)
- `employee_id`: Bound Employee ID (locked via Agent Identity)
- `authenticated_user_email`: User email address
- `active_intent`: Current conversation intent (`"POLICY_QA"`, `"PTO_REQUEST"`, `"INCIDENT_TICKET"`, `"MEDICAL_LEAVE_WORKFLOW"`)
- `last_booked_pto_id`: Request ID of last submitted PTO (e.g. `"PTO-9876"`) for compensating rollbacks
- `last_created_ticket_id`: Ticket ID of last created ServiceImmediately ticket (e.g. `"INC-54321"`)

---

## 5. Quality & Evaluation Benchmarks

- **Target Q&A Accuracy**: `>= 95%` precision (0% hallucination)
- **Target Response Latency**: `< 10.0 seconds` (Safety guardrail overhead `< 300ms`)
- **Target Throughput**: `>= 50 QPS`
- **Evalset Stratification (4-Tier Recipe)**:
  - `40%` Happy Path / Direct Lookups
  - `30%` Gotchas & Cross-System Orchestrations
  - `15%` Hallucination Baits
  - `15%` Out-of-Scope Probes

---

## 6. Strict Prohibition of Hardcoded Values & Mock Data

To enforce strict tenant isolation, identity security, and production accuracy, all agents and tools must adhere to the following zero-hardcoding rules:

1. **Zero Hardcoded Identifiers & Fallbacks**:
   - Never hardcode static employee IDs (e.g. `EMP-26`, `EMP-1004`, `EMP-dulee`), static user emails, or default fallback constants in tool logic, sub-agent tools, or orchestrators.
   - All employee IDs and user emails must be dynamically resolved from the authenticated user's session context (`x-goog-authenticated-user-email` / `X-MCP-Token`) or live remote FastMCP API calls (`get_current_employee_id()`).

2. **Zero Mock Data & Fake Database Generators**:
   - Never construct local dummy database dictionaries (e.g. `EMPLOYEE_DATABASE`), fake data generators (e.g. `_get_or_create_employee`), or hardcoded numeric balances (e.g. `vacation_accrued: 20.0`).
   - Every tool call must pass through directly to the live remote FastMCP / REST backend endpoints and stream the raw response. If a remote API call fails, return the actual error response; do not fall back to mock data.
