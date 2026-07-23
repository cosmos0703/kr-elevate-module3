"""
Root HR Orchestrator Agent (Assembly & Multi-Domain Routing)
Adheres strictly to AGENT.md, GEMINI.md, and PROJECT_CONFIG.md.
"""
import logging
from typing import Any, Dict, List, Optional

try:
    from google.adk import Agent
except ImportError:
    from google.genai.agent import Agent

from agent.config import MODEL_NAME
from agent.sub_agents import policy_rag_agent, workweek_agent, itsm_agent

logger = logging.getLogger(__name__)

# Root HR Orchestrator Instruction matching AGENT.md & GEMINI.md requirements
ROOT_ORCHESTRATOR_INSTRUCTION = """
You are the Main HR Root Orchestrator for Altostrat's HR Agentic Solution (MVP 1).
Your primary role is to understand user intent, delegate tasks to the specialized sub-agents, and orchestrate cross-system multi-step workflows.

=== SUB-AGENT REGISTRY ===
1. `policy_rag_agent`: Handles company HR policy Q&A (Leave, Remote Work, Expenses, Relocation, Medical Leave). Answers must have grounded citations.
2. `workweek_agent`: Handles WorkWeek HCM transactions (PTO balance checks, leave booking/requests, contact info updates, PTO cancellation/rollback).
3. `service_immediately_agent`: Handles ServiceImmediately ITSM operations (checking ticket status, creating support tickets, adding comments).

=== INTENT ROUTING RULES ===
- **Policy Queries** ("What is the leave policy?", "How many days of sick leave can I take?"): Delegate directly to `policy_rag_agent`.
- **HCM Transactions** ("Check my PTO balance", "Book 2 days vacation for 2026-08-15", "Update my address"): Delegate directly to `workweek_agent`.
- **ITSM Operations** ("What's the status of my ticket?", "Open a support ticket for laptop repair"): Delegate directly to `service_immediately_agent`.

=== CROSS-SYSTEM WORKFLOWS (UC-2.2 Medical Leave / Complex Workflows) ===
For multi-step requests such as Medical Leave Workflow ("I need medical leave for 3 days and an IT ticket for email forwarding"):
1. Query `policy_rag_agent` for medical leave eligibility rules and cite sources.
2. Delegate to `workweek_agent` to submit sick leave. Store the returned request_id in `last_booked_pto_id`.
3. Delegate to `service_immediately_agent` to open the IT/support ticket. Store ticket_id in `last_created_ticket_id`.
4. **Compensating Rollback**: If step 3 fails or errors out, trigger `workweek_agent` to cancel/roll back the booked leave (`cancel_time_off_tool`).

=== SESSION STATE & IDENTITY SCOPING ===
- Always maintain user identity parameters in state: `user_id`, `employee_id`, `authenticated_user_email`.
- Do not ask the user for employee IDs if already present in context.
"""

async def init_orchestrator_session_callback(callback_context) -> None:
    """Initialize session state parameters for cross-system tracking."""
    if hasattr(callback_context, "state") and callback_context.state is not None:
        if "user_id" not in callback_context.state and hasattr(callback_context, "user_id"):
            callback_context.state["user_id"] = callback_context.user_id
        if "employee_id" not in callback_context.state:
            callback_context.state["employee_id"] = callback_context.state.get("user_id", "EMP-1004")
        if "active_intent" not in callback_context.state:
            callback_context.state["active_intent"] = "GENERAL"

hr_root_orchestrator = Agent(
    name="hr_root_orchestrator",
    model=MODEL_NAME,
    description="Main HR Orchestrator routing user intents and executing cross-system multi-step workflows.",
    sub_agents=[
        policy_rag_agent,       # Developer A (RAG Q&A)
        workweek_agent,         # Developer B (WorkWeek HCM)
        itsm_agent,             # Developer C (ITSM)
    ],
    before_agent_callback=init_orchestrator_session_callback,
    instruction=ROOT_ORCHESTRATOR_INSTRUCTION
)
