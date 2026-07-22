# AGENT.md - Multi-Agent System Rules & Implementation Spec

This document governs the implementation of the **Hierarchical Multi-Agent System** for the HR Agentic Solution (MVP 1) in accordance with [PROJECT_CONFIG.md](file:///usr/local/google/home/inhyep/work/kr-elevate-module3/PROJECT_CONFIG.md).

---

## 1. Multi-Agent Topology & Sub-Agent Registry

All agents in `agent/sub_agents/` and `agent/root_orchestrator.py` must adhere to the registered contract names and model configuration:

```
                          ┌───────────────────────────┐
                          │   hr_root_orchestrator    │
                          │   (Root Orchestrator)     │
                          └─────────────┬─────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
┌─────────────────────────┐┌─────────────────────────┐┌─────────────────────────┐
│    policy_rag_agent     ││     workweek_agent      ││service_immediately_agent│
│ (Developer A - RAG Q&A) ││(Developer B - WorkWeek) ││ (Developer C - ITSM)    │
└─────────────────────────┘└─────────────────────────┘└─────────────────────────┘
```

### Agent Specifications Table

| Agent Symbol | ADK `name` | Model | Description | Tools Assigned |
| :--- | :--- | :--- | :--- | :--- |
| `policy_rag_agent` | `policy_rag_agent` | `gemini-3.5-flash` | `"Answers employee questions about company HR policies (Leave, Remote Work, Expense, Relocation) with grounded citations."` | `policy_search_tool` |
| `workweek_agent` | `workweek_agent` | `gemini-3.5-flash` | `"Handles WorkWeek HCM transactions: PTO balances, personal contact updates, and leave booking."` | `get_employee_balances_tool`, `request_time_off_tool`, `update_contact_tool` |
| `itsm_agent` | `service_immediately_agent` | `gemini-3.5-flash` | `"Handles ServiceImmediately ITSM operations: ticket status queries, incident creation, and comments."` | `create_ticket_tool`, `list_tickets_tool`, `update_ticket_status_tool` |
| `hr_root_orchestrator` | `hr_root_orchestrator` | `gemini-3.5-flash` | `"Main HR Orchestrator routing user intents and executing cross-system multi-step workflows."` | Sub-agents: `policy_rag_agent`, `workweek_agent`, `itsm_agent` |

---

## 2. Shared Session State Protocol (`session.state`)

When reading or updating multi-turn session state across agents and tools, developers must read/write to these standardized keys:

```python
# Session State Key Standards
session.state["user_id"]                  # e.g., "EMP-1004"
session.state["employee_id"]              # Bound Employee ID (locked via Agent Identity)
session.state["authenticated_user_email"] # e.g., "inhyep@gcp.altostrat.com"
session.state["active_intent"]            # "POLICY_QA" | "PTO_REQUEST" | "INCIDENT_TICKET" | "MEDICAL_LEAVE_WORKFLOW"
session.state["last_booked_pto_id"]       # e.g., "PTO-9876" (Used for rollback compensation)
session.state["last_created_ticket_id"]   # e.g., "INC-54321"
```

---

## 3. Cross-System Workflow & Compensating Transaction Rules

For complex multi-step workflows (e.g. **UC-2.2 Medical Leave Workflow**):

1. **Step 1 (Policy RAG)**: Retrieve and quote medical leave policy with verified markdown link citation.
2. **Step 2 (WorkWeek)**: Submit Sick leave via `request_time_off_tool` -> Save returned `request_id` into `session.state["last_booked_pto_id"]`.
3. **Step 3 (ITSM)**: Create IT ticket via `create_ticket_tool` for email forwarding.
4. **Compensating Rollback Trigger**: If Step 3 fails (network timeout/error), trigger `DELETE /work-week/api/employees/{id}/timeoff/requests/{last_booked_pto_id}` to cancel the submitted PTO and maintain data consistency.
