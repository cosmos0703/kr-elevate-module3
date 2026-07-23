"""
ServiceImmediately ITSM Sub-Agent (Owner: Developer C)
"""
try:
    from google.adk.agents import Agent
except ImportError:
    from google.adk import Agent
from agent.config import MODEL_NAME
from agent.tools.itsm_mcp import (
    create_ticket_tool,
    list_tickets_tool,
    update_ticket_status_tool,
    add_ticket_comment_tool,
    create_ticket,
    list_tickets,
    update_ticket_status,
    add_ticket_comment,
)

async def init_user_id_callback(callback_context) -> None:
    user_id = getattr(callback_context, "user_id", None) or callback_context.state.get("user_id") or callback_context.state.get("employee_id")
    if user_id:
        callback_context.state["user_id"] = user_id
        callback_context.state["employee_id"] = user_id

itsm_agent = Agent(
    name="service_immediately_agent",
    model=MODEL_NAME,
    description="Handles ServiceImmediately ITSM operations: ticket status queries, incident creation, and comments.",
    tools=[
        create_ticket_tool,
        list_tickets_tool,
        update_ticket_status_tool,
        add_ticket_comment_tool,
    ],
    before_agent_callback=init_user_id_callback,
    instruction="""
    You are the ServiceImmediately ITSM Sub-Agent. You handle IT and HRSD support ticket tracking, creation, updates, and comments.
    
    The authenticated employee ID of the current user is '{user_id}'.
    
    Rules:
    - When asked to check the status of your tickets or list incident tickets, you must immediately call list_tickets_tool with requested_by set to '{user_id}'. Do not ask the user for their name or email address.
    - Answer status checks in a concise, direct sentence (e.g. "Your VPN connection ticket INC-54321 is currently In Progress.").
    - When creating a ticket, always require requested_by, category, short_description, and priority. Enforce priority guardrails: '1 - Critical' priority requires the description to contain outage, crash, or downtime keywords.
    - Use add_ticket_comment_tool to post comments on a ticket.
    - Use update_ticket_status_tool to transition the ticket lifecycle (New -> In Progress -> Resolved -> Closed).
    """
)
