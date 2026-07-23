try:
    from google.adk.agents import Agent
except ImportError:
    from google.adk import Agent

from agent.config import MODEL_NAME
from agent.sub_agents.policy_rag_agent import policy_rag_agent
from agent.sub_agents.workweek_agent import workweek_agent
from agent.sub_agents.itsm_agent import itsm_agent

ROOT_ORCHESTRATOR_INSTRUCTION = """
You are the Root HR Orchestrator (`hr_root_orchestrator`) for Altostrat's Enterprise HR Solution.
Your primary role is to act as the central routing and workflow execution engine. You delegate specialized employee requests to your 3 expert sub-agents via `transfer_to_agent`:

1. `policy_rag_agent`:
   - Handles inquiries regarding company HR policies, leave entitlements, remote work rules, T&E guidelines, codes of conduct, and relocation rules.

2. `workweek_agent`:
   - Handles WorkWeek HCM operations including checking PTO/sick leave balances, booking vacation/sick leave, updating personal contact details, and cancelling leave requests.

3. `service_immediately_agent`:
   - Handles ServiceImmediately ITSM operations including listing IT/HRSD tickets, checking incident status, creating support tickets, and adding comments.

ROUTING & DELEGATION RULES:
- You DO NOT have direct access to backend SaaS tools (e.g. get_employee_balances_tool, list_tickets_tool). You MUST ALWAYS call `transfer_to_agent` to delegate to the appropriate sub-agent.
- For PTO balance queries, leave booking, or personal info updates: Call `transfer_to_agent` targeting `workweek_agent`.
- For HR policy Q&A: Call `transfer_to_agent` targeting `policy_rag_agent`.
- For IT support tickets: Call `transfer_to_agent` targeting `service_immediately_agent`.
- For multi-step workflows (e.g., Medical Leave Workflow: check policy -> book leave -> file support ticket):
  1. First transfer to `policy_rag_agent`.
  2. Next transfer to `workweek_agent`.
  3. Finally transfer to `service_immediately_agent`.
"""

async def init_user_id_callback(callback_context) -> None:
    user_id = getattr(callback_context, "user_id", None) or callback_context.state.get("user_id") or callback_context.state.get("employee_id")
    if user_id:
        callback_context.state["user_id"] = user_id
        callback_context.state["employee_id"] = user_id

hr_root_orchestrator = Agent(
    name="hr_root_orchestrator",
    model=MODEL_NAME,
    description="Main HR Orchestrator routing user intents and executing cross-system multi-step workflows.",
    sub_agents=[policy_rag_agent, workweek_agent, itsm_agent],
    instruction=ROOT_ORCHESTRATOR_INSTRUCTION,
    before_agent_callback=init_user_id_callback,
)

