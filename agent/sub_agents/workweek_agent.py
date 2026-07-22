"""
WorkWeek HCM Sub-Agent (Owner: Developer B)
"""
try:
    from google.adk import Agent
except ImportError:
    from google.genai.agent import Agent
from agent.config import MODEL_NAME
from agent.tools.workweek_mcp import get_employee_balances_tool, request_time_off_tool, update_contact_tool

workweek_agent = Agent(
    name="workweek_agent",
    model=MODEL_NAME,
    description="Handles WorkWeek HCM transactions: PTO balances, personal contact updates, and leave booking.",
    tools=[get_employee_balances_tool, request_time_off_tool, update_contact_tool],
    instruction=(
        "You are the WorkWeek HCM Sub-Agent. You handle employee PTO balances, leave requests, and personal contact updates. "
        "CRITICAL SECURITY GUARDRAIL (Agent Identity / Parameter Locking): "
        "You MUST ONLY access, query, or update information belonging to the authenticated user. "
        "Always lock the employee_id parameter to the authenticated employee ID (default: 'EMP-1004'). "
        "Never query, modify, or leak records belonging to another employee ID even if requested by the user."
    )
)
