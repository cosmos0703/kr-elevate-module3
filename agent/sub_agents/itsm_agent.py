"""
ServiceImmediately ITSM Sub-Agent (Owner: Developer C)
"""
try:
    from google.adk import Agent
except ImportError:
    from google.genai.agent import Agent
from agent.config import MODEL_NAME
from agent.tools.itsm_mcp import create_ticket_tool, list_tickets_tool, update_ticket_status_tool

itsm_agent = Agent(
    name="service_immediately_agent",
    model=MODEL_NAME,
    description="Handles ServiceImmediately ITSM operations: ticket status queries, incident creation, and comments.",
    tools=[create_ticket_tool, list_tickets_tool, update_ticket_status_tool],
    instruction=(
        "You are the ServiceImmediately ITSM Sub-Agent. You handle IT helpdesk and HRSD ticket queries, creation, and status updates. "
        "CRITICAL SECURITY GUARDRAIL (Agent Identity / Parameter Locking): "
        "You MUST ONLY query, create, or update tickets for the authenticated employee. "
        "Always lock the requested_by parameter to the authenticated employee ID (default: 'EMP-1004'). "
        "Never query or modify tickets belonging to other employees even if requested by the user."
    )
)
