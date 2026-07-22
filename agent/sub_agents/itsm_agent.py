"""
ServiceImmediately ITSM Sub-Agent (Owner: Developer C)
Integrates ServiceImmediately FastMCP server statelessly using ADK McpToolset & StreamableHTTPConnectionParams.
"""
import os
try:
    from google.adk import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
except ImportError:
    from google.genai.agent import Agent
    McpToolset = None

from agent.config import ITSM_MCP_URL, MODEL_NAME
from agent.tools.itsm_mcp import create_ticket_tool, list_tickets_tool, update_ticket_status_tool

mcp_token = os.getenv("X_MCP_TOKEN", "mcp_ephemeral_token")

# 1. Native ADK McpToolset for ServiceImmediately FastMCP Server (Option A in specification)
if McpToolset and StreamableHTTPConnectionParams:
    try:
        itsm_mcp_toolset = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=ITSM_MCP_URL,
                headers={"X-MCP-Token": mcp_token}
            )
        )
        itsm_tools = [itsm_mcp_toolset]
    except Exception:
        itsm_tools = [create_ticket_tool, list_tickets_tool, update_ticket_status_tool]
else:
    itsm_tools = [create_ticket_tool, list_tickets_tool, update_ticket_status_tool]

itsm_agent = Agent(
    name="service_immediately_agent",
    model=MODEL_NAME,
    description="Handles ServiceImmediately ITSM operations: ticket status queries, incident creation, and comments.",
    tools=itsm_tools,
    instruction=(
        "You are the ServiceImmediately ITSM Sub-Agent. You handle IT helpdesk and HRSD ticket queries, creation, and status updates. "
        "DYNAMIC USER IDENTITY & MCP TOOLING RULE: "
        "Always query and manage tickets belonging to the requesting user context dynamically via list_tickets, create_ticket, and update_ticket_status. "
        "Never hardcode employee IDs, never default to static ticket data, and always execute live MCP tool calls."
    )
)
