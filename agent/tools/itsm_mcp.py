"""
ServiceImmediately ITSM FastMCP Tool Integration (Owner: Developer C / Developer B)
"""
import os
import json
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from agent.config import ITSM_MCP_URL

async def _call_itsm_mcp(tool_name: str, arguments: dict):
    # Retrieve X-MCP-Token from environment if needed, otherwise use a placeholder
    token = os.getenv("X_MCP_TOKEN", "mock_token")
    headers = {"X-MCP-Token": token}
    
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        async with streamable_http_client(ITSM_MCP_URL, http_client=client) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                if result.isError:
                    raise RuntimeError(f"MCP Tool {tool_name} returned error: {result.content}")
                
                # Parse content
                if result.content and hasattr(result.content[0], "text"):
                    text_data = result.content[0].text
                    try:
                        return json.loads(text_data)
                    except json.JSONDecodeError:
                        return {"result": text_data}
                return {}

async def list_tickets_tool(requested_by: str) -> list:
    """
    Queries ticket list and status timelines in ServiceImmediately.
    """
    res = await _call_itsm_mcp("list_tickets", {"employee_id": requested_by})
    if isinstance(res, list):
        return res
    elif isinstance(res, dict) and "tickets" in res:
        return res["tickets"]
    return [res]

async def create_ticket_tool(requested_by: str, category: str, short_description: str, priority: str = "3 - Moderate") -> dict:
    """
    Opens an incident or support ticket in ServiceImmediately ITSM.
    """
    # 1. Priority Verification Guardrail: Critical priority must describe active outage/crash/downtime
    if priority == "1 - Critical":
        desc_lower = short_description.lower()
        if not any(kw in desc_lower for kw in ["outage", "crash", "downtime"]):
            return {
                "status": "FAILED",
                "error": "Critical priority tickets must describe an active outage, crash, or system downtime keyword."
            }
            
    # 2. Call MCP create_ticket tool
    return await _call_itsm_mcp("create_ticket", {
        "requested_by": requested_by,
        "category": category,
        "short_description": short_description,
        "priority": priority,
        "assignment_group": "Service Desk"
    })

async def update_ticket_status_tool(ticket_id: str, status: str) -> dict:
    """
    Updates lifecycle status of an ITSM ticket.
    """
    return await _call_itsm_mcp("update_ticket_status", {
        "ticket_id": ticket_id,
        "status": status,
        "resolution_notes": "Updated via ITSM Agent",
        "updated_by": "System"
    })

async def add_ticket_comment_tool(ticket_id: str, author: str, comment: str) -> dict:
    """
    Appends a timeline comment to the ticket's activity log in ServiceImmediately.
    """
    return await _call_itsm_mcp("add_ticket_comment", {
        "ticket_id": ticket_id,
        "author": author,
        "comment": comment
    })

# Tool function aliases matching both MCP and local naming conventions
list_tickets = list_tickets_tool
create_ticket = create_ticket_tool
update_ticket_status = update_ticket_status_tool
add_ticket_comment = add_ticket_comment_tool

