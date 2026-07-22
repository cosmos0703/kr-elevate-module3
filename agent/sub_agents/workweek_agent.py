"""
WorkWeek HCM Sub-Agent (Owner: Developer B)
"""
from google.genai.agent import Agent
from agent.config import MODEL_NAME
from agent.tools.workweek_mcp import get_employee_balances_tool, request_time_off_tool, update_contact_tool

workweek_agent = Agent(
    name="workweek_agent",
    model=MODEL_NAME,
    description="Handles WorkWeek HCM transactions: PTO balances, personal contact updates, and leave booking.",
    tools=[get_employee_balances_tool, request_time_off_tool, update_contact_tool],
    instruction="Interact with WorkWeek MCP. Always enforce employee_id parameter lock from user context."
)
