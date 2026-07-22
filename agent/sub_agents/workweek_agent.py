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
        "CRITICAL DYNAMIC AGENT IDENTITY RULE: "
        "Extract the employee ID dynamically from the user's input or context (e.g. 'EMP-13', 'EMP-1004'). "
        "If the user specifies an employee ID or asks for their own balances, pass that exact employee_id dynamically to get_employee_balances_tool. "
        "If no employee ID is mentioned by the user, default to passing 'EMP-13'. "
        "Never hardcode responses and always return live data from the tool."
    )
)
