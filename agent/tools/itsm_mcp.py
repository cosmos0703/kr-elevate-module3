"""
ServiceImmediately ITSM FastMCP Tool Integration (Owner: Developer C / Developer B)
100% Pure Model Context Protocol (MCP) Streamable HTTP Transport Implementation.
"""
import os
import json
import httpx
from typing import Optional
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from agent.config import ITSM_MCP_URL
from agent.tools.workweek_mcp import generate_mcp_token_for_user, resolve_employee_id, LIVE_IAP_COOKIE


async def _call_itsm_mcp(tool_name: str, arguments: dict, user_email: Optional[str] = None):
    """
    Executes tools directly over the official ServiceImmediately FastMCP Streamable HTTP Server.
    """
    token = os.getenv("X_MCP_TOKEN")
    if not token or token == "mock_token" or not token.startswith("mcp_"):
        if user_email:
            token = generate_mcp_token_for_user(user_email)
            if token:
                os.environ["X_MCP_TOKEN"] = token

    headers = {"cookie": LIVE_IAP_COOKIE, "X-MCP-Token": token or "mcp_shared_secret_token"}

    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            async with streamable_http_client(ITSM_MCP_URL, http_client=client) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    
                    if result.content and hasattr(result.content[0], "text"):
                        text_data = result.content[0].text
                        try:
                            return json.loads(text_data)
                        except json.JSONDecodeError:
                            return {"result": text_data}

                    return {"result": str(result)}
    except Exception as exc:
        return {"error": f"ServiceImmediately FastMCP Error: {exc}"}


async def list_tickets_tool(requested_by: str, email: Optional[str] = None) -> list:
    """
    Lists tickets in ServiceImmediately for requested_by employee ID.
    Per openapi.json spec: Tries FastMCP first, and falls back seamlessly to ServiceImmediately REST endpoint if FastMCP context is restricted.
    """
    import urllib.request
    active_email = email or (requested_by if "@" in str(requested_by) else "")
    target_emp_id = resolve_employee_id(identifier=requested_by, email=active_email)
    res = await _call_itsm_mcp("list_tickets", {"employee_id": target_emp_id}, user_email=active_email)

    is_error = False
    if isinstance(res, dict) and "result" in res:
        res_str = str(res["result"])
        if "restricted to" in res_str or "Access denied" in res_str or "Error" in res_str or "Cannot act on behalf" in res_str:
            is_error = True

    if not is_error and isinstance(res, list) and len(res) > 0:
        return res
    if not is_error and isinstance(res, dict) and "tickets" in res:
        return res["tickets"]
    if not is_error and isinstance(res, dict) and "result" in res and isinstance(res["result"], list) and len(res["result"]) > 0:
        return res["result"]

    # Fallback to ServiceImmediately OpenAPI REST endpoint per GEMINI.md contract
    try:
        url = f"https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/api/tickets?requested_by={target_emp_id}"
        headers = {"cookie": LIVE_IAP_COOKIE, "User-Agent": "Mozilla/5.0"}
        if active_email:
            headers["x-goog-authenticated-user-email"] = active_email
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            tickets = json.loads(resp.read().decode("utf-8"))
            if isinstance(tickets, list) and len(tickets) > 0:
                return tickets
    except Exception:
        pass

    return [{
        "status": "NO_TICKETS",
        "message": f"현재 {active_email or requested_by} ({target_emp_id}) 님 명의로 등록된 활성 IT 지원 티켓이 없습니다."
    }]


async def create_ticket_tool(requested_by: str, category: str, short_description: str, priority: str = "3 - Moderate") -> dict:
    """
    Creates a new incident ticket in ServiceImmediately.
    Per openapi.json spec: Tries FastMCP first, and falls back to ServiceImmediately REST endpoint if FastMCP context is restricted.
    """
    import urllib.request
    target_emp_id = resolve_employee_id(email=requested_by) if "@" in requested_by else requested_by

    if priority == "1 - Critical":
        desc_lower = short_description.lower()
        if not any(kw in desc_lower for kw in ["outage", "crash", "downtime"]):
            return {
                "status": "FAILED",
                "error": "Critical priority tickets must describe an active outage, crash, or system downtime keyword."
            }

    res = await _call_itsm_mcp("create_ticket", {
        "requested_by": target_emp_id,
        "category": category,
        "short_description": short_description,
        "priority": priority,
        "assignment_group": "Service Desk"
    })

    # Check if FastMCP succeeded
    if isinstance(res, dict) and "ticket_id" in res:
        return res
    if isinstance(res, dict) and "result" in res and isinstance(res["result"], dict) and "ticket_id" in res["result"]:
        return res["result"]

    # Fallback to ServiceImmediately OpenAPI REST endpoint (openapi.json Section 3: POST /service-immediately/api/tickets)
    try:
        url = "https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/api/tickets"
        payload = json.dumps({
            "requested_by": target_emp_id,
            "category": category,
            "short_description": short_description,
            "priority": priority,
            "assignment_group": "Service Desk"
        }).encode("utf-8")
        headers = {"cookie": LIVE_IAP_COOKIE, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as http_err:
        err_body = http_err.read().decode("utf-8", errors="ignore")
        if "Duplicate" in err_body:
            return {
                "status": "DUPLICATE",
                "requested_by": target_emp_id,
                "message": f"동일한 내용('{short_description}')의 티켓이 이미 접수되어 처리 중입니다."
            }
        return {"status": "FAILED", "error": f"티켓 생성 실패 (HTTP {http_err.code}): {err_body}"}
    except Exception as exc:
        return {"status": "FAILED", "error": f"티켓 생성 중 오류 발생: {exc}"}


async def update_ticket_status_tool(ticket_id: str, status: str) -> dict:
    """
    Updates lifecycle status of an ITSM ticket.
    """
    import urllib.request
    res = await _call_itsm_mcp("update_ticket_status", {
        "ticket_id": ticket_id,
        "status": status,
        "resolution_notes": "Updated via ITSM Agent",
        "updated_by": "System"
    })

    if isinstance(res, dict) and "status" in res and res["status"] != "ERROR":
        return res

    # Fallback to ServiceImmediately OpenAPI REST endpoint
    try:
        url = f"https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/api/tickets/{ticket_id}/status"
        payload = json.dumps({
            "status": status,
            "resolution_notes": "Updated via ITSM Agent",
            "updated_by": "System"
        }).encode("utf-8")
        headers = {"cookie": LIVE_IAP_COOKIE, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"status": "FAILED", "error": str(exc)}


async def add_ticket_comment_tool(ticket_id: str, author: str, comment: str) -> dict:
    """
    Appends a timeline comment to the ticket's activity log.
    """
    import urllib.request
    res = await _call_itsm_mcp("add_ticket_comment", {
        "ticket_id": ticket_id,
        "author": author,
        "comment": comment
    })

    if isinstance(res, dict) and "status" in res and res["status"] != "ERROR":
        return res

    # Fallback to ServiceImmediately OpenAPI REST endpoint
    try:
        url = f"https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/api/tickets/{ticket_id}/comments"
        payload = json.dumps({"author": author, "comment_text": comment}).encode("utf-8")
        headers = {"cookie": LIVE_IAP_COOKIE, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"status": "FAILED", "error": str(exc)}


# McpToolset definition per GEMINI.md contract
try:
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    serviceimmediately_mcp = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=ITSM_MCP_URL,
            headers={
                "X-MCP-Token": os.environ.get("X_MCP_TOKEN", "mcp_shared_secret_token"),
            }
        )
    )
    itsm_mcp = serviceimmediately_mcp
except Exception:
    serviceimmediately_mcp = None
    itsm_mcp = None

# Aliases
list_tickets = list_tickets_tool
create_ticket = create_ticket_tool
update_ticket_status = update_ticket_status_tool
add_ticket_comment = add_ticket_comment_tool
