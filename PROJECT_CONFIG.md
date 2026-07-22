# **PROJECT_CONFIG.md - HR Agentic Solution (MVP 1)**

This document defines the **unified project parameters, naming conventions, infrastructure configurations, and shared contracts** that all 3 developers (and their AI coding agents) must strictly adhere to.

---

## **1. Unified Project & Infrastructure Parameters**

| Parameter Key | Unified Value | Notes / Environment Variable |
| :--- | :--- | :--- |
| **GCP Project ID** | `aiproject-429506-hr-policies` | `GOOGLE_CLOUD_PROJECT` |
| **GCP Region** | `us-central1` | `GOOGLE_CLOUD_REGION` |
| **Default LLM Model** | `gemini-2.5-flash` | `MODEL_NAME` |
| **Vector Embedding Model** | `text-embedding-004` (768 dimensions) | `EMBEDDING_MODEL` |
| **Session Hydration Store** | Google Cloud Firestore / Redis | `FIRESTORE_DATABASE_ID` |
| **Audit Compliance Store** | Google Cloud Spanner | `SPANNER_INSTANCE_ID` |
| **Key Vaulting** | Google Secret Manager | `SECRET_MANAGER_PROJECT_ID` |

---

## **2. Unified Sub-Agent Contracts (Names & Descriptions)**

All agents must use the exact `name` and `description` strings below to ensure seamless routing by the Root Orchestrator.

| Agent Variable Name | ADK Agent `name` | Exact `description` | Primary Owner |
| :--- | :--- | :--- | :---: |
| **`policy_rag_agent`** | `policy_rag_agent` | `"Answers employee questions about company HR policies (Leave, Remote Work, Expense, Relocation) with grounded citations."` | **Developer A** |
| **`workweek_agent`** | `workweek_agent` | `"Handles WorkWeek HCM transactions: PTO balances, personal contact updates, and leave booking."` | **Developer B** |
| **`itsm_agent`** | `service_immediately_agent` | `"Handles ServiceImmediately ITSM operations: ticket status queries, incident creation, and comments."` | **Developer C** |
| **`hr_root_orchestrator`** | `hr_root_orchestrator` | `"Main HR Orchestrator routing user intents and executing cross-system multi-step workflows."` | **Root / Assembly** |

---

## **3. Backend Subsystem Protocols & Headers**

| Subsystem | Integration Protocol | Base Endpoint URL | Auth Header / Secret Key |
| :--- | :--- | :--- | :--- |
| **WorkWeek (MCP)** | FastMCP Streamable HTTP | `/work-week/mcp/` | `X-MCP-Token: <ephemeral_token>` |
| **WorkWeek (REST)** | REST API | `/work-week/api/employees/{id}/` | `x-goog-authenticated-user-email` |
| **ServiceImmediately** | FastMCP Streamable HTTP | `/service-immediately/mcp/` | `X-MCP-Token: <ephemeral_token>` |
| **Policy Vector Store** | Local Vector Search | Local Embeddings | N/A |

---

## **4. Shared Session State Keys**

When reading or updating multi-turn session state (`session.state`), developers must use the following standard keys:

- `user_id`: Authenticated Employee ID (e.g. `"EMP-1004"`)
- `employee_id`: Bound Employee ID (locked via Agent Identity)
- `authenticated_user_email`: User email address
- `active_intent`: Current conversation intent (`"POLICY_QA"`, `"PTO_REQUEST"`, `"INCIDENT_TICKET"`, `"MEDICAL_LEAVE_WORKFLOW"`)
- `last_booked_pto_id`: Request ID of last submitted PTO (e.g. `"PTO-9876"`) for compensating rollbacks
- `last_created_ticket_id`: Ticket ID of last created ServiceImmediately ticket (e.g. `"INC-54321"`)

---

## **5. Quality & Evaluation Benchmarks**

- **Target Q&A Accuracy**: `>= 95%` precision (0% hallucination)
- **Target Response Latency**: `< 10.0 seconds` (Safety overhead `< 300ms`)
- **Target Throughput**: `>= 50 QPS`
- **Evalset Stratification (4-Tier Recipe)**:
  - `40%` Happy Path / Direct Lookups
  - `30%` Gotchas & Cross-System Orchestrations
  - `15%` Hallucination Baits
  - `15%` Out-of-Scope Probes
