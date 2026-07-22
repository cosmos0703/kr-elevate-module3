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
    instruction="Interact with ServiceImmediately MCP for IT and HRSD ticket management."
)
