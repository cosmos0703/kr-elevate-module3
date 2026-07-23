"""
Root Orchestrator Agent (Assembly & Multi-Domain Routing)
Adheres to PROJECT_CONFIG.md and WorkWeek HCM specifications.
"""
from typing import Any, List, Optional
from agent.config import MODEL_NAME
from agent.sub_agents.workweek_agent import workweek_agent

try:
    from google.genai.agent import Agent
except ImportError:
    try:
        from google.adk.agents import Agent
    except ImportError:
        class Agent:  # type: ignore
            def __init__(self, name: str, model: str = "", description: str = "", tools: Optional[List[Any]] = None, sub_agents: Optional[List[Any]] = None, instruction: str = ""):
                self.name = name
                self.model = model
                self.description = description
                self.tools = tools or []
                self.sub_agents = sub_agents or []
                self.instruction = instruction

hr_root_orchestrator = Agent(
    name="hr_root_orchestrator",
    model=MODEL_NAME,
    description="Main HR Orchestrator routing user intents to WorkWeek HCM Sub-Agent.",
    sub_agents=[
        workweek_agent,         # WorkWeek HCM
    ],
    instruction="""Main HR Orchestrator:
    - Route employee queries and leave requests to WorkWeek HCM Sub-Agent.
    """
)


def handle_root_chat(
    user_prompt: str,
    email: Optional[str] = None,
    employee_id: Optional[str] = None,
    session_state: Optional[dict] = None,
) -> dict:
    """
    Main HR Orchestrator entrypoint.
    Receives user email and employee_id, maintains session state, and delegates to WorkWeek sub-agent.
    """
    if session_state is None:
        session_state = {}

    from agent.sub_agents.workweek_agent import handle_workweek_chat_simulation, resolve_employee_id

    active_email = email or (employee_id if (employee_id and "@" in str(employee_id)) else "inhyep@google.com")
    resolved_id = resolve_employee_id(employee_id, email=active_email)

    session_state["authenticated_user_email"] = active_email
    session_state["employee_id"] = resolved_id
    session_state["user_id"] = resolved_id

    return handle_workweek_chat_simulation(
        user_prompt=user_prompt,
        employee_id=resolved_id,
        email=active_email,
        session_state=session_state,
    )
