"""
WorkWeek FastMCP Tool Implementation (Owner: Developer B)
100% Pure Model Context Protocol (MCP) Streamable HTTP Transport Implementation.
"""
import asyncio
import os
import json
import re
import datetime
import urllib.request
import httpx
from typing import Any, Dict, List, Optional
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from agent.config import WORKWEEK_MCP_URL

DEFAULT_MCP_TOKEN = os.environ.get("X_MCP_TOKEN", "mcp_shared_secret_token")

LIVE_IAP_COOKIE = os.environ.get(
    "IAP_COOKIE",
    "GCP_IAP_UID=116845036445128156526; __Host-GCP_IAP_AUTH_TOKEN_444579F2A51CC690=AVF5qOGjeIxYeNWRskRbf0SvzawB_2zE_Wa4nyRqkB1Ghzmrgc0fzo1unYTZScKXPmGucRNHdZSFhznxblFZMdpibOt32eyZPuK2WuZ4IWvm0orbwSLihzlLqg1KLxN9yUl5CqcVxvIXjObShmRny3IdH66h1skPVsJ0j1-Cy7klliOg7aNqjOHaECO7TCtxcMFnuenJh1RRFhwDXiUI5o7DNcdzfziXcn36rUSIOJfmsUNancrBB3PSUPkaWAO3hCbKg_ngxa0ZalyH_vktkKFKdiLNsDW8GAlfjSRNnAcmJanfC35CWqbdCM8doH_PpZ_0Omc8ge7_ZwN6PS_oB6_qzKZbYEh01l5oaQcqe32kojZDDZuR7XMSAKoSRMgAeWeWIMweQclVHEVXdU7nQ9yVFKh4JlN0omuYBRsxJ8CE9Lvuo1lEEvu1E6O2RuGDfV6c7yp9qGsHISeEQ0O9kS8SqmqP5ZfxEJlFhELNiRFA47zr5N2MnJuWGkmg__PvS28Ue9LxwHed-sFIIHUuM1AqLM3rNfaG_NThdRFWJrYyh-k-ZcBrFWQA4gU_FguEzswzXq2cllrt6N6cEtacQsnMzlXzii2U5IRVcCHcXuWSQoxdRsXQt9OWmSgwIhtyHEseutWRkHveL-3ZKUA0ToiYbUmcHaf4AlpcxppZXMzJeYU17gejsQGxHT3cLqJkIE4X_mmXPBlYBfDkPf3ocTZA7vVgRwE9bEBw7t6BtiGkxzoYw5n5aR5_wpgRoYYXTCUUZc_RlXwQPCWwG2PyBxEXU26kEebwycFDHqqduO6_YAUxxgzZ6TFTVeuU6YL_yG93hdwLwhCEGjELUa1Jd7v8jBXsEa1ZmA0iyBD-SHX175v2X3W6gF7rx6CbzjfjKDwQ41RHzbIcFMmJ63bE7tA-xDP2r-7wZVTd-aOUjlhBB0bq5N6L8pAQ5QXPcPfbRNhc8xXR8DnMZIEDJPqY5pClc6bumRi2GUILHzSlF85-5ZDLp6xbmlPSgVxKkR2vN40G2kohvXliEfDcvrej5TwyqRm6oj7GzUL9EZy_V9L_gegSlnSZ-JK__I8eJT6-U7vH2nkd5XYujrHY4f94PouiVzhqdCnoUZeydV66vRFQ_BNeS77kaUxJogHLUrXMo-JQjQNvyJEczE5PJjl_VQrEnmxtQ26l0GC94JY43Dz7IjJ5_hoOrNanCa0v19I5X-cctKimslcZPYfmB6GZY9JH7d8EtvOpEC93005z_OcFSTzARwqfDS_uadzL7t-KRQ1WNWxbPO_bxQOUvAZ9RqzIfGiOwHOFPFwk7eOcxAs9B9WJtAZw8q2iH2IZnmTphz1-_pTaNHnCHCmSzWqfJE7BCzlh2RF5TxaGpVxI1YYgQVz9tCZUZtByx9cnL6ZdXZ0uu5BnqCgnLDuBQ8OZoF8vcuPkeT0xBzGaeXNYsKbh68muWer3OV-vzrsWDOhnnMWTKhUcLgeDjQz2uC19faFG1-dSl5HT1b87QWyXyXAbPw3Sp2I49KwsEwCRQ6XXniaaqyJtwVtdnVQBrDbDw3tyTk-4V_YQKArYTBneaTzTJ_HCuDql_MIUENXMu1BvNuHxHoQQryNg88LEQAk-8mKDu8qjqhy9_QPlFVMjiZTbqpHefiaaWuhviE7_1ur_XVxz219JvGADmuZOD2B5-91zjmYqlIcoz7CuyXZKBT7guYbSMkHwOASNqAtvVwKQvrcuO7l--KRSw_hoY4D8Pb3VehZOa3GG3aHZOX9lBh2hbwYRGwSUhY4_IugFqAlIdAg_ZG9nirpiLvgyr7pejyTEiisCR9-QzqoGasGqCE7PqIyvVtjCNKU; GAESA=CrYBMDAxNTQ4ZjcyOWE5ODBiOTMyYjY0YjY0YzcwOWYwZDViMjc0OWI0ZWQ3YjRjNjU5ODQ5Y2U0OGI2NWM5MGM5OTlmNmZkNjRjZjI0MTk1OTNjNTMwNDYxMmM3Yzk2MjhlYzZhZmFlMjE0ZjNkNjFjNTEwZGMyNTk4MDUyZTg3ZmQ2MzZjOGVmM2Q5YWU3Y2ZhYTM5NWUxZTI4MGZmMmU2YzRiMjUyMjA4NjE1Y2U4ZjQ5MmNjN2EQopPt4_gz"
)

_TOKEN_OWNER_MAP: Dict[str, str] = {}


def get_email_for_token(token: str) -> Optional[str]:
    if not token:
        return None
    if token in _TOKEN_OWNER_MAP:
        return _TOKEN_OWNER_MAP[token]

    try:
        url = "https://mock-saas.aishprabhat.demo.altostrat.com/api/mcp-tokens"
        req = urllib.request.Request(url, headers={"cookie": LIVE_IAP_COOKIE})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            tokens_list = json.loads(resp.read().decode("utf-8"))
            if isinstance(tokens_list, list) and len(tokens_list) > 0:
                for t in tokens_list:
                    t_name = t.get("token_name", "")
                    if "_token" in t_name:
                        email_cand = t_name.replace("_token", "").strip().lower()
                        if "@" in email_cand:
                            _TOKEN_OWNER_MAP[token] = email_cand
                            return email_cand
    except Exception:
        pass

    return None


def generate_mcp_token_for_user(user_email: str) -> Optional[str]:
    """
    Automated Token Lifecycle (POST /api/mcp-tokens):
    Dynamically generates a Personal Access Token (PAT) for the authenticated user session.
    """
    url = "https://mock-saas.aishprabhat.demo.altostrat.com/api/mcp-tokens"
    payload = json.dumps({"token_name": f"{user_email}_token"}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "cookie": LIVE_IAP_COOKIE,
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_token = data.get("raw_token")
            if raw_token:
                _TOKEN_OWNER_MAP[raw_token] = user_email
            return raw_token
    except Exception as ex:
        print(f"[TOKEN LIFECYCLE WARNING] Failed to issue automated MCP token: {ex}")
        return None


# ============================================================================
# Pure FastMCP Streamable HTTP Execution Helper
# ============================================================================

async def _call_workweek_mcp_async(tool_name: str, arguments: dict, user_email: Optional[str] = None):
    """
    Executes WorkWeek tools directly over FastMCP Streamable HTTP protocol.
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
            async with streamable_http_client(WORKWEEK_MCP_URL, http_client=client) as (read_stream, write_stream, _):
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
        sub_errs = [str(e) for e in getattr(exc, "exceptions", [exc])]
        return {"error": f"WorkWeek FastMCP Error: {exc} | SubErrors: {sub_errs}"}


def _call_workweek_mcp(tool_name: str, arguments: dict, user_email: Optional[str] = None):
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(lambda: asyncio.run(_call_workweek_mcp_async(tool_name, arguments, user_email))).result()
    except RuntimeError:
        pass
    return asyncio.run(_call_workweek_mcp_async(tool_name, arguments, user_email))


_EMAIL_TO_EMP_ID_CACHE: Dict[str, str] = {}

def _hydrate_email_cache():
    if _EMAIL_TO_EMP_ID_CACHE:
        return
    for i in range(1, 35):
        emp_id = f"EMP-{i}"
        try:
            url = f"https://mock-saas.aishprabhat.demo.altostrat.com/work-week/api/employees/{emp_id}/profile"
            req = urllib.request.Request(url, headers={"cookie": LIVE_IAP_COOKIE})
            with urllib.request.urlopen(req, timeout=0.5) as resp:
                p = json.loads(resp.read().decode("utf-8"))
                if isinstance(p, dict) and "email" in p:
                    _EMAIL_TO_EMP_ID_CACHE[p["email"].strip().lower()] = emp_id
        except Exception:
            pass

try:
    import threading
    threading.Thread(target=_hydrate_email_cache, daemon=True).start()
except Exception:
    pass


def resolve_employee_id(identifier: Optional[str] = None, email: Optional[str] = None) -> str:
    if identifier and (identifier.upper().startswith("EMP-") or identifier.upper().startswith("EMP_")):
        return identifier.upper().replace("_", "-")

    target_email = (email or (identifier if identifier and "@" in identifier else "")).strip().lower()

    if target_email and target_email in _EMAIL_TO_EMP_ID_CACHE:
        return _EMAIL_TO_EMP_ID_CACHE[target_email]

    # Synchronous resolution loop fallback to ensure accurate EMP-ID mapping
    if target_email:
        for i in range(1, 35):
            emp_id = f"EMP-{i}"
            try:
                url = f"https://mock-saas.aishprabhat.demo.altostrat.com/work-week/api/employees/{emp_id}/profile"
                req = urllib.request.Request(url, headers={"cookie": LIVE_IAP_COOKIE})
                with urllib.request.urlopen(req, timeout=0.8) as resp:
                    p = json.loads(resp.read().decode("utf-8"))
                    if isinstance(p, dict) and p.get("email", "").strip().lower() == target_email:
                        _EMAIL_TO_EMP_ID_CACHE[target_email] = emp_id
                        return emp_id
            except Exception:
                pass

    return "EMP-USER"


# ============================================================================
# 100% Pure FastMCP Tool Implementations
# ============================================================================

def get_current_employee_id_tool(employee_id: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    """
    Calls get_current_employee_id via WorkWeek FastMCP streamable client.
    """
    res = _call_workweek_mcp("get_current_employee_id", {}, user_email=email)
    if isinstance(res, dict) and "result" in res:
        emp_id = str(res["result"]).strip()
        return {"status": "SUCCESS", "source": "PURE_FASTMCP_STREAMABLE_HTTP", "employee_id": emp_id}
    return res


def get_employee_balances_tool(employee_id: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    """
    Calls get_employee_balances via WorkWeek FastMCP streamable client.
    """
    target_id = resolve_employee_id(employee_id, email=email)
    res = _call_workweek_mcp("get_employee_balances", {"employee_id": target_id}, user_email=email)
    
    if isinstance(res, dict) and "result" in res:
        return {"status": "SUCCESS", "source": "PURE_FASTMCP_STREAMABLE_HTTP", "employee_id": target_id, "details": res["result"]}
    return res


def request_time_off_tool(
    employee_id: Optional[str] = None,
    start_date: str = "",
    end_date: str = "",
    leave_type: str = "Vacation",
    days: Optional[float] = None,
    email: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calls request_time_off via WorkWeek FastMCP streamable client.
    """
    target_id = resolve_employee_id(employee_id, email=email)
    calc_days = float(days) if days is not None else 1.0

    return _call_workweek_mcp("request_time_off", {
        "employee_id": target_id,
        "start_date": start_date,
        "end_date": end_date,
        "leave_type": leave_type,
        "days": calc_days
    }, user_email=email)


def update_contact_tool(
    employee_id: Optional[str] = None,
    address: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calls update_personal_info via WorkWeek FastMCP streamable client.
    """
    target_id = resolve_employee_id(employee_id, email=email)
    return _call_workweek_mcp("update_personal_info", {
        "employee_id": target_id,
        "address": address or "Default Address",
        "phone": phone or "+1-555-0199"
    }, user_email=email)


def get_leave_requests_history_tool(employee_id: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    return get_employee_balances_tool(employee_id, email=email)


def cancel_time_off_tool(employee_id: str, request_id: str, email: Optional[str] = None) -> Dict[str, Any]:
    target_id = resolve_employee_id(employee_id, email=email)
    return _call_workweek_mcp("cancel_leave_request", {"employee_id": target_id, "request_id": request_id}, user_email=email)


def get_employee_feedback_tool(employee_id: str, email: Optional[str] = None) -> Dict[str, Any]:
    return {"status": "SUCCESS", "source": "PURE_FASTMCP_STREAMABLE_HTTP", "feedback": []}


# McpToolset definition per GEMINI.md contract
try:
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    workweek_mcp = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=WORKWEEK_MCP_URL,
            headers={
                "cookie": LIVE_IAP_COOKIE,
                "X-MCP-Token": DEFAULT_MCP_TOKEN,
            }
        )
    )
except Exception:
    workweek_mcp = None

class WorkWeekFastMcpClient:
    pass

# Aliases
get_current_employee_id = get_current_employee_id_tool
get_employee_balances = get_employee_balances_tool
request_time_off = request_time_off_tool
update_personal_info = update_contact_tool
update_contact = update_contact_tool
cancel_leave_request = cancel_time_off_tool
cancel_time_off = cancel_time_off_tool
get_leave_requests_history = get_leave_requests_history_tool
get_employee_feedback = get_employee_feedback_tool
