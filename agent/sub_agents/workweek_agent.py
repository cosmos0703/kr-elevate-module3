"""
WorkWeek HCM Sub-Agent (Owner: Developer B)
Integrates WorkWeek FastMCP server statelessly using ADK McpToolset & StreamableHTTPConnectionParams.
"""
import os
try:
    from google.adk import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
except ImportError:
    from google.genai.agent import Agent
    McpToolset = None

from agent.config import MODEL_NAME, WORKWEEK_MCP_URL
from agent.tools.workweek_mcp import get_employee_balances_tool, request_time_off_tool, update_contact_tool

mcp_token = os.getenv("X_MCP_TOKEN", "mcp_ephemeral_token")

# 1. Native ADK McpToolset for WorkWeek FastMCP Server (Option A in specification)
if McpToolset and StreamableHTTPConnectionParams:
    try:
        workweek_mcp_toolset = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=WORKWEEK_MCP_URL,
                headers={"X-MCP-Token": mcp_token}
            )
        )
        workweek_tools = [workweek_mcp_toolset]
    except Exception:
        workweek_tools = [get_employee_balances_tool, request_time_off_tool, update_contact_tool]
else:
    workweek_tools = [get_employee_balances_tool, request_time_off_tool, update_contact_tool]

workweek_agent = Agent(
    name="workweek_agent",
    model=MODEL_NAME,
    description="Handles WorkWeek HCM transactions: PTO balances, personal contact updates, and leave booking.",
    tools=workweek_tools,
    instruction=(
        "You are the WorkWeek HCM Sub-Agent. You handle employee PTO balances, leave requests, and personal contact updates. "
        "DYNAMIC USER IDENTITY & MCP TOOLING RULE: "
        "First, invoke get_current_employee_id() dynamically to resolve the authenticated user session's employee ID. "
        "Use the resolved employee ID for all subsequent calls (get_employee_balances, request_time_off, update_personal_info). "
        "Never hardcode employee IDs, never default to static values, and always return real live data from the tools."
    )
)
