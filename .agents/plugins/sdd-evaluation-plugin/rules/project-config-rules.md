# Project Config Rules (HR Agentic Solution MVP 1)

These rules apply across all evaluations, agent code reviews, and drift audits to ensure strict adherence to `PROJECT_CONFIG.md`.

## 1. Project Parameter Verification

- **GCP Project ID**: Must be `pe-kor-trainer` (Environment: `GOOGLE_CLOUD_PROJECT`).
- **GCP Project Number**: Must be `775423734296` (Environment: `GOOGLE_CLOUD_PROJECT_NUMBER`).
- **Region**: Must be `global` (Environment: `GOOGLE_CLOUD_REGION`).
- **Default LLM**: Must be configured as `gemini-3.5-flash` (`MODEL_NAME`).
- **Vector Embedding Model**: Must be `text-embedding-004` (768 dimensions).

## 2. Sub-Agent Naming and Description Standards

Evaluators and code generators must enforce exact matches for ADK Agent configurations:

| Variable | Exact `name` | Exact `description` |
| :--- | :--- | :--- |
| `policy_rag_agent` | `policy_rag_agent` | `Answers employee questions about company HR policies (Leave, Remote Work, Expense, Relocation) with grounded citations.` |
| `workweek_agent` | `workweek_agent` | `Handles WorkWeek HCM transactions: PTO balances, personal contact updates, and leave booking.` |
| `itsm_agent` | `service_immediately_agent` | `Handles ServiceImmediately ITSM operations: ticket status queries, incident creation, and comments.` |
| `hr_root_orchestrator` | `hr_root_orchestrator` | `Main HR Orchestrator routing user intents and executing cross-system multi-step workflows.` |

## 3. Session State Key Compliance

All multi-turn state manipulations must use the canonical keys:
- `user_id`
- `employee_id`
- `authenticated_user_email`
- `active_intent`
- `last_booked_pto_id`
- `last_created_ticket_id`

## 4. Evaluation Targets

- **Q&A Accuracy**: `>= 95%`
- **Response Latency**: `< 10.0s` (Guardrails `< 300ms`)
- **Throughput**: `>= 50 QPS`
- **4-Tier Stratification**: 40% Happy Path / 30% Gotchas & Cross-System / 15% Hallucination Baits / 15% Out-of-Scope.
