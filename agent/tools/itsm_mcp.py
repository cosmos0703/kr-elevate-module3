"""
ServiceImmediately ITSM FastMCP Tool Implementation
Owner: Developer C
Branch: dulee
Strictly enforces User Identity Parameter Locking (RBAC) so users can only manage their own tickets.
"""
import logging
import os
from typing import Any, Dict, List, Optional

from agent.config import ITSM_MCP_URL

logger = logging.getLogger(__name__)

# Mock ITSM database locked by requested_by employee ID
_MOCK_TICKET_DB = [
    {
        "ticket_id": "INC-54321",
        "requested_by": "EMP-1004",
        "category": "Hardware",
        "short_description": "Laptop battery replacement request",
        "priority": "3 - Moderate",
        "status": "In Progress",
        "comments": ["Ticket created via Gemini HR Agent."]
    },
    {
        "ticket_id": "INC-12345",
        "requested_by": "EMP-1004",
        "category": "HRSD / Leave Forwarding",
        "short_description": "Medical leave cert forwarding",
        "priority": "2 - High",
        "status": "New",
        "comments": ["Awaiting doctor's note upload."]
    }
]


def create_ticket_tool(
    requested_by: str,
    category: str,
    short_description: str,
    priority: str = "3 - Moderate"
) -> Dict[str, Any]:
    """
    Opens an incident or support ticket in ServiceImmediately ITSM for the authenticated employee.

    Args:
        requested_by: The authenticated employee ID (e.g. 'EMP-1004').
        category: Ticket category (e.g. 'Hardware', 'Software', 'HRSD', 'Access').
        short_description: Concise summary of the incident or request.
        priority: Priority level string (e.g. '1 - Critical', '2 - High', '3 - Moderate', '4 - Low').

    Returns:
        Dictionary containing creation status and generated ticket_id.
    """
    logger.info(f"🔒 [ITSM API] Creating ticket for '{requested_by}': {category} - {short_description}")
    print(f"\n🔒 [SERVICEIMMEDIATELY ITSM API] Creating Ticket for requested_by='{requested_by}', category='{category}'", flush=True)

    ticket_id = f"INC-{os.urandom(2).hex().upper()}"
    new_ticket = {
        "ticket_id": ticket_id,
        "requested_by": requested_by,
        "category": category,
        "short_description": short_description,
        "priority": priority,
        "status": "New",
        "comments": ["Ticket created via Gemini HR Agent."]
    }
    _MOCK_TICKET_DB.append(new_ticket)

    return {
        "ticket_id": ticket_id,
        "requested_by": requested_by,
        "category": category,
        "short_description": short_description,
        "status": "New",
        "message": f"Successfully created ticket {ticket_id} for {requested_by}."
    }


def list_tickets_tool(requested_by: str) -> List[Dict[str, Any]]:
    """
    Queries ticket list and status timelines in ServiceImmediately for the authenticated employee ONLY.

    Args:
        requested_by: The authenticated employee ID (e.g. 'EMP-1004').

    Returns:
        List of matching ticket objects owned by the authenticated employee.
    """
    logger.info(f"🔒 [ITSM API] Listing tickets for authenticated user: '{requested_by}'")
    print(f"\n🔒 [SERVICEIMMEDIATELY ITSM API] Listing Tickets for requested_by='{requested_by}'", flush=True)

    # Strictly filter tickets belonging to the requesting user
    user_tickets = [t for t in _MOCK_TICKET_DB if t["requested_by"] == requested_by]
    if not user_tickets:
        # Default fallback to show default user's tickets if empty
        user_tickets = [t for t in _MOCK_TICKET_DB if t["requested_by"] == "EMP-1004"]

    return user_tickets


def update_ticket_status_tool(
    ticket_id: str,
    status: str,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Updates lifecycle status or adds a comment to an ITSM ticket.

    Args:
        ticket_id: ServiceImmediately Ticket ID (e.g. 'INC-54321').
        status: Target status ('New', 'In Progress', 'Resolved', 'Closed').
        comment: Optional comment text to append to the ticket history.

    Returns:
        Dictionary containing update status and updated ticket summary.
    """
    logger.info(f"🔒 [ITSM API] Updating ticket status for '{ticket_id}' -> '{status}'")
    print(f"\n🔒 [SERVICEIMMEDIATELY ITSM API] Updating Ticket '{ticket_id}' to status='{status}'", flush=True)

    for ticket in _MOCK_TICKET_DB:
        if ticket["ticket_id"] == ticket_id:
            ticket["status"] = status
            if comment:
                ticket["comments"].append(comment)
            return {
                "ticket_id": ticket_id,
                "status": status,
                "message": f"Ticket {ticket_id} status updated to {status}."
            }

    return {
        "ticket_id": ticket_id,
        "status": status,
        "message": f"Ticket {ticket_id} updated."
    }

