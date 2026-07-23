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


# ============================================================================
# Synchronous & Asynchronous Chat Handlers for FastAPI Server & Web UI
# ============================================================================
from typing import Optional, Dict, Any
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

_session_service = InMemorySessionService()
_runner = Runner(agent=hr_root_orchestrator, app_name="hr_enterprise_app", session_service=_session_service)
_user_session_map: Dict[str, Any] = {}


from agent.tools.workweek_mcp import resolve_employee_id

async def handle_root_chat_async(user_message: str, email: Optional[str] = None, employee_id: Optional[str] = None) -> Dict[str, Any]:
    resolved_id = employee_id or resolve_employee_id(email=email)
    user_key = email or resolved_id
    if user_key not in _user_session_map:
        session = await _session_service.create_session(app_name="hr_enterprise_app", user_id=resolved_id)
        _user_session_map[user_key] = session

    session = _user_session_map[user_key]
    msg = types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
    
    reply_text = ""
    author = "hr_root_orchestrator"
    
    async for event in _runner.run_async(user_id=resolved_id, session_id=session.id, new_message=msg):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    reply_text = part.text
                    if event.author:
                        author = event.author

    return {
        "reply": reply_text or "요청이 정상 처리되었습니다.",
        "author": author,
        "status": "SUCCESS"
    }


def handle_root_chat(user_message: str, email: Optional[str] = None, employee_id: Optional[str] = None) -> Dict[str, Any]:
    import asyncio
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(lambda: asyncio.run(handle_root_chat_async(user_message, email=email, employee_id=employee_id)))
        return future.result()

