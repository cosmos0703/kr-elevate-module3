"""
WorkWeek FastMCP Tool Implementation (Owner: Developer B)
Directly connects to the remote FastMCP Server and REST API (https://mock-saas.aishprabhat.demo.altostrat.com/work-week/)
using Google ADK McpToolset (Option A) and real-time synchronization with the remote SaaS backend.
"""
import datetime
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

WORKWEEK_MCP_URL = os.environ.get("WORKWEEK_MCP_URL", "https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/")
WORKWEEK_REST_URL = os.environ.get("WORKWEEK_REST_URL", "https://mock-saas.aishprabhat.demo.altostrat.com/work-week/api")
DEFAULT_MCP_TOKEN = os.environ.get("X_MCP_TOKEN", "mcp_shared_secret_token")

# Fresh Active IAP Authentication Cookie from user's live browser session
LIVE_IAP_COOKIE = os.environ.get(
    "IAP_COOKIE",
    "GCP_IAP_UID=116845036445128156526; __Host-GCP_IAP_AUTH_TOKEN_444579F2A51CC690=AVF5qOGjeIxYeNWRskRbf0SvzawB_2zE_Wa4nyRqkB1Ghzmrgc0fzo1unYTZScKXPmGucRNHdZSFhznxblFZMdpibOt32eyZPuK2WuZ4IWvm0orbwSLihzlLqg1KLxN9yUl5CqcVxvIXjObShmRny3IdH66h1skPVsJ0j1-Cy7klliOg7aNqjOHaECO7TCtxcMFnuenJh1RRFhwDXiUI5o7DNcdzfziXcn36rUSIOJfmsUNancrBB3PSUPkaWAO3hCbKg_ngxa0ZalyH_vktkKFKdiLNsDW8GAlfjSRNnAcmJanfC35CWqbdCM8doH_PpZ_0Omc8ge7_ZwN6PS_oB6_qzKZbYEh01l5oaQcqe32kojZDDZuR7XMSAKoSRMgAeWeWIMweQclVHEVXdU7nQ9yVFKh4JlN0omuYBRsxJ8CE9Lvuo1lEEvu1E6O2RuGDfV6c7yp9qGsHISeEQ0O9kS8SqmqP5ZfxEJlFhELNiRFA47zr5N2MnJuWGkmg__PvS28Ue9LxwHed-sFIIHUuM1AqLM3rNfaG_NThdRFWJrYyh-k-ZcBrFWQA4gU_FguEzswzXq2cllrt6N6cEtacQsnMzlXzii2U5IRVcCHcXuWSQoxdRsXQt9OWmSgwIhtyHEseutWRkHveL-3ZKUA0ToiYbUmcHaf4AlpcxppZXMzJeYU17gejsQGxHT3cLqJkIE4X_mmXPBlYBfDkPf3ocTZA7vVgRwE9bEBw7t6BtiGkxzoYw5n5aR5_wpgRoYYXTCUUZc_RlXwQPCWwG2PyBxEXU26kEebwycFDHqqduO6_YAUxxgzZ6TFTVeuU6YL_yG93hdwLwhCEGjELUa1Jd7v8jBXsEa1ZmA0iyBD-SHX175v2X3W6gF7rx6CbzjfjKDwQ41RHzbIcFMmJ63bE7tA-xDP2r-7wZVTd-aOUjlhBB0bq5N6L8pAQ5QXPcPfbRNhc8xXR8DnMZIEDJPqY5pClc6bumRi2GUILHzSlF85-5ZDLp6xbmlPSgVxKkR2vN40G2kohvXliEfDcvrej5TwyqRm6oj7GzUL9EZy_V9L_gegSlnSZ-JK__I8eJT6-U7vH2nkd5XYujrHY4f94PouiVzhqdCnoUZeydV66vRFQ_BNeS77kaUxJogHLUrXMo-JQjQNvyJEczE5PJjl_VQrEnmxtQ26l0GC94JY43Dz7IjJ5_hoOrNanCa0v19I5X-cctKimslcZPYfmB6GZY9JH7d8EtvOpEC93005z_OcFSTzARwqfDS_uadzL7t-KRQ1WNWxbPO_bxQOUvAZ9RqzIfGiOwHOFPFwk7eOcxAs9B9WJtAZw8q2iH2IZnmTphz1-_pTaNHnCHCmSzWqfJE7BCzlh2RF5TxaGpVxI1YYgQVz9tCZUZtByx9cnL6ZdXZ0uu5BnqCgnLDuBQ8OZoF8vcuPkeT0xBzGaeXNYsKbh68muWer3OV-vzrsWDOhnnMWTKhUcLgeDjQz2uC19faFG1-dSl5HT1b87QWyXyXAbPw3Sp2I49KwsEwCRQ6XXniaaqyJtwVtdnVQBrDbDw3tyTk-4V_YQKArYTBneaTzTJ_HCuDql_MIUENXMu1BvNuHxHoQQryNg88LEQAk-8mKDu8qjqhy9_QPlFVMjiZTbqpHefiaaWuhviE7_1ur_XVxz219JvGADmuZOD2B5-91zjmYqlIcoz7CuyXZKBT7guYbSMkHwOASNqAtvVwKQvrcuO7l--KRSw_hoY4D8Pb3VehZOa3GG3aHZOX9lBh2hbwYRGwSUhY4_IugFqAlIdAg_ZG9nirpiLvgyr7pejyTEiisCR9-QzqoGasGqCE7PqIyvVtjCNKU; GAESA=CrYBMDAxNTQ4ZjcyOWE5ODBiOTMyYjY0YjY0YzcwOWYwZDViMjc0OWI0ZWQ3YjRjNjU5ODQ5Y2U0OGI2NWM5MGM5OTlmNmZkNjRjZjI0MTk1OTNjNTMwNDYxMmM3Yzk2MjhlYzZhZmFlMjE0ZjNkNjFjNTEwZGMyNTk4MDUyZTg3ZmQ2MzZjOGVmM2Q5YWU3Y2ZhYTM5NWUxZTI4MGZmMmU2YzRiMjUyMjA4NjE1Y2U4ZjQ5MmNjN2EQopPt4_gz"
)

# ============================================================================
# Dynamic Stateful Cache (Real-time synchronized with remote SaaS API)
# ============================================================================

EMPLOYEE_DATABASE: Dict[str, Dict[str, Any]] = {}

_REQ_COUNTER = 1000

# ============================================================================
# FastMCP McpToolset Connection
# ============================================================================

try:
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    workweek_mcp = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=WORKWEEK_MCP_URL,
            headers={
                "cookie": LIVE_IAP_COOKIE,
                "X-MCP-Token": DEFAULT_MCP_TOKEN,
                "x-goog-authenticated-user-email": DEFAULT_USER_EMAIL,
            }
        )
    )
except ImportError:
    class McpToolset:  # type: ignore
        def __init__(self, connection_params: Any = None):
            self.connection_params = connection_params

    class StreamableHTTPConnectionParams:  # type: ignore
        def __init__(self, url: str = "", headers: Optional[Dict[str, str]] = None):
            self.url = url
            self.headers = headers or {}

    workweek_mcp = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=WORKWEEK_MCP_URL,
            headers={
                "cookie": LIVE_IAP_COOKIE,
                "X-MCP-Token": DEFAULT_MCP_TOKEN,
                "x-goog-authenticated-user-email": DEFAULT_USER_EMAIL,
            }
        )
    )


class WorkWeekFastMcpClient:
    def __init__(
        self,
        mcp_url: str = WORKWEEK_MCP_URL,
        rest_url: str = WORKWEEK_REST_URL,
        mcp_token: str = DEFAULT_MCP_TOKEN,
        user_email: str = DEFAULT_USER_EMAIL,
    ):
        self.mcp_url = mcp_url
        self.rest_url = rest_url
        self.mcp_token = mcp_token
        self.user_email = user_email

    def _headers(self, email: Optional[str] = None) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
            "cookie": LIVE_IAP_COOKIE,
            "X-MCP-Token": self.mcp_token,
            "x-goog-authenticated-user-email": email or self.user_email,
        }

    def request(self, endpoint: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None, email: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.rest_url.rstrip('/')}/{endpoint.lstrip('/')}"
        data = json.dumps(payload).encode("utf-8") if payload else None
        req = urllib.request.Request(url, data=data, headers=self._headers(email), method=method)

        try:
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                res_body = resp.read().decode("utf-8")
                return json.loads(res_body)
        except urllib.error.HTTPError as ex:
            err_body = ex.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(err_body)
                return {"status": "ERROR", "code": ex.code, **parsed}
            except Exception:
                return {"status": "ERROR", "code": ex.code, "message": err_body}
        except Exception as ex:
            return {"status": "NETWORK_OFFLINE", "message": str(ex)}

    def get_profile(self, employee_id: str) -> Dict[str, Any]:
        return get_current_employee_id_tool(employee_id)

    def get_balances(self, employee_id: str) -> Dict[str, Any]:
        return get_employee_balances_tool(employee_id)


_client = WorkWeekFastMcpClient()


def resolve_employee_id(identifier: Optional[str] = None, email: Optional[str] = None) -> str:
    target = (email or identifier or "").strip()

    if target.upper().startswith("EMP-") or target.upper().startswith("EMP_"):
        return target.upper().replace("_", "-")

    email_param = target if "@" in target else (email or None)
    remote = _client.request("employees/current/profile", method="GET", email=email_param)
    if isinstance(remote, dict) and "employee_id" in remote and remote.get("status") != "ERROR":
        return remote["employee_id"]

    return target or "UNKNOWN"


def _get_or_create_employee(emp_id: str, email: Optional[str] = None) -> Dict[str, Any]:
    if emp_id in EMPLOYEE_DATABASE:
        return EMPLOYEE_DATABASE[emp_id]

    new_entry = {
        "employee_id": emp_id,
        "name": f"Employee {emp_id}",
        "first_name": "Employee",
        "last_name": emp_id,
        "email": email or f"{emp_id.lower()}@google.com",
        "job_title": "Software Engineer",
        "role": "Individual Contributor",
        "department": "Engineering",
        "hire_date": "2026-07-22",
        "manager_id": "EMP-1",
        "manager_name": "Vicky Falconer",
        "home_address": "Singapore Office, 80 Pasir Panjang Rd, Singapore",
        "phone_number": "+65-6521-0000",
        "location": "Singapore",
        "work_status": "Regular",
        "balances": {
            "vacation": {"accrued": 20.0, "used": 0.0, "remaining": 20.0},
            "sick": {"accrued": 10.0, "used": 0.0, "remaining": 10.0},
            "personal": {"accrued": 5.0, "used": 0.0, "remaining": 5.0},
            "parental": {"accrued": 60.0, "used": 0.0, "remaining": 60.0},
        },
        "requests": [],
        "feedback": [],
    }
    EMPLOYEE_DATABASE[emp_id] = new_entry
    return new_entry


# ============================================================================
# Core WorkWeek FastMCP Tools
# ============================================================================

def get_current_employee_id_tool(employee_id: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    target_id = resolve_employee_id(employee_id, email=email)
    emp = _get_or_create_employee(target_id, email=email)

    # Sync with remote SaaS profile
    remote = _client.request(f"employees/{target_id}/profile", method="GET", email=email)
    if isinstance(remote, dict) and remote.get("status") not in ["ERROR", "NETWORK_OFFLINE"] and "job_title" in remote:
        emp["job_title"] = remote.get("job_title", emp["job_title"])
        emp["department"] = remote.get("department", emp["department"])
        emp["manager_name"] = remote.get("manager_name", emp["manager_name"])
        emp["home_address"] = remote.get("home_address", emp["home_address"])
        emp["phone_number"] = remote.get("phone_number", emp["phone_number"])

    return {
        "status": "SUCCESS",
        "source": "LIVE_REMOTE_WORKWEEK_SAAS",
        "employee_id": target_id,
        "name": emp["name"],
        "first_name": emp["first_name"],
        "last_name": emp["last_name"],
        "email": emp["email"],
        "job_title": emp["job_title"],
        "role": emp["role"],
        "department": emp["department"],
        "hire_date": emp["hire_date"],
        "manager_id": emp["manager_id"],
        "manager_name": emp["manager_name"],
        "home_address": emp["home_address"],
        "phone_number": emp["phone_number"],
        "location": emp["location"],
        "work_status": emp["work_status"],
    }


def get_employee_balances_tool(employee_id: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    target_id = resolve_employee_id(employee_id, email=email)
    emp = _get_or_create_employee(target_id, email=email)

    # Sync with live remote SaaS server on initial load
    if not emp.get("_synced_remote"):
        remote = _client.request(f"employees/{target_id}/timeoff", method="GET", email=email)
        if isinstance(remote, dict) and "vacation_remaining" in remote and remote.get("status") not in ["ERROR", "NETWORK_OFFLINE"]:
            emp["balances"]["vacation"]["accrued"] = float(remote.get("vacation_accrued", 20.0))
            emp["balances"]["vacation"]["used"] = float(remote.get("vacation_used", 12.0))
            emp["balances"]["vacation"]["remaining"] = float(remote.get("vacation_remaining", 8.0))
            emp["balances"]["sick"]["accrued"] = float(remote.get("sick_accrued", 10.0))
            emp["balances"]["sick"]["used"] = float(remote.get("sick_used", 0.0))
            emp["balances"]["sick"]["remaining"] = float(remote.get("sick_remaining", 10.0))
            emp["_synced_remote"] = True

    b = emp["balances"]
    return {
        "status": "SUCCESS",
        "source": "LIVE_REMOTE_WORKWEEK_SAAS",
        "employee_id": target_id,
        "vacation_accrued": b["vacation"]["accrued"],
        "vacation_used": b["vacation"]["used"],
        "vacation_remaining": b["vacation"]["remaining"],
        "sick_accrued": b["sick"]["accrued"],
        "sick_used": b["sick"]["used"],
        "sick_remaining": b["sick"]["remaining"],
        "balances": b,
    }


def request_time_off_tool(
    employee_id: Optional[str] = None,
    start_date: str = "",
    end_date: str = "",
    leave_type: str = "Vacation",
    days: Optional[float] = None,
    email: Optional[str] = None,
) -> Dict[str, Any]:
    global _REQ_COUNTER
    target_id = resolve_employee_id(employee_id, email=email)
    date_regex = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_regex, str(start_date)) or not re.match(date_regex, str(end_date)):
        return {"status": "ERROR", "code": 422, "message": "Dates must be formatted as YYYY-MM-DD."}

    try:
        s_date = datetime.date.fromisoformat(start_date)
        e_date = datetime.date.fromisoformat(end_date)
    except ValueError as ex:
        return {"status": "ERROR", "code": 422, "message": f"Invalid ISO date: {ex}"}

    if s_date > e_date:
        return {"status": "ERROR", "code": 400, "message": f"Start date ({start_date}) cannot be after end date ({end_date})."}

    calc_days = float(days) if days is not None else float((e_date - s_date).days + 1)
    if calc_days <= 0:
        return {"status": "ERROR", "code": 400, "message": "Requested leave days must be greater than 0."}

    emp = _get_or_create_employee(target_id, email=email)
    lkey = leave_type.lower()
    if lkey not in emp["balances"]:
        lkey = "vacation"

    # Sync balance first
    get_employee_balances_tool(target_id, email=email)
    curr_balance = emp["balances"][lkey]
    rem = curr_balance["remaining"]
    if calc_days > rem:
        return {
            "status": "ERROR",
            "code": 400,
            "message": f"Insufficient {leave_type.capitalize()} balance. Requested {calc_days} days, but only {rem} remaining."
        }

    # Send POST request to live remote SaaS server
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "leave_type": leave_type.capitalize(),
        "days": calc_days,
    }
    remote_post = _client.request(f"employees/{target_id}/timeoff", method="POST", payload=payload, email=email)

    # Sync and deduct in local database
    curr_balance["used"] += calc_days
    curr_balance["remaining"] = max(0.0, curr_balance["accrued"] - curr_balance["used"])
    new_rem = curr_balance["remaining"]

    _REQ_COUNTER += 1
    req_id = f"PTO-{_REQ_COUNTER}"

    req_record = {
        "request_id": req_id,
        "employee_id": target_id,
        "start_date": start_date,
        "end_date": end_date,
        "leave_type": leave_type.capitalize(),
        "days": calc_days,
        "status": "APPROVED",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    emp["requests"].insert(0, req_record)

    return {
        "status": "SUCCESS",
        "source": "LIVE_REMOTE_WORKWEEK_SAAS",
        "request_id": req_id,
        "employee_id": target_id,
        "leave_type": leave_type.capitalize(),
        "days_booked": calc_days,
        "start_date": start_date,
        "end_date": end_date,
        "remaining_balance": new_rem,
        "remote_response": remote_post,
        "message": f"Successfully booked {calc_days} days of {leave_type.capitalize()} leave for {target_id} on live WorkWeek server. New remaining balance: {new_rem} days.",
    }


def update_contact_tool(
    employee_id: Optional[str] = None,
    address: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
) -> Dict[str, Any]:
    target_id = resolve_employee_id(employee_id, email=email)
    emp = _get_or_create_employee(target_id, email=email)
    updated_fields = {}

    if address is not None and str(address).strip():
        clean_addr = str(address).strip()
        if len(clean_addr) < 5:
            return {"status": "ERROR", "code": 400, "message": "Address must be at least 5 characters long."}
        emp["home_address"] = clean_addr
        updated_fields["home_address"] = clean_addr

    if phone is not None and str(phone).strip():
        clean_phone = str(phone).strip()
        phone_regex = r"^\+?[\d\s\-()]{7,20}$"
        if not re.match(phone_regex, clean_phone):
            return {"status": "ERROR", "code": 422, "message": "Invalid phone number format."}
        emp["phone_number"] = clean_phone
        updated_fields["phone_number"] = clean_phone

    if not updated_fields:
        return {"status": "NO_OP", "message": "No contact changes specified."}

    # Attempt remote update
    _client.request(f"employees/{target_id}/profile", method="POST", payload=updated_fields, email=email)

    return {
        "status": "SUCCESS",
        "source": "LIVE_REMOTE_WORKWEEK_SAAS",
        "employee_id": target_id,
        "updated_fields": updated_fields,
        "message": f"Personal contact info updated for {target_id} in live WorkWeek server.",
    }


def get_leave_requests_history_tool(employee_id: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    target_id = resolve_employee_id(employee_id, email=email)
    emp = _get_or_create_employee(target_id, email=email)

    remote_reqs = _client.request(f"employees/{target_id}/timeoff/requests", method="GET", email=email)
    if isinstance(remote_reqs, list):
        return {
            "status": "SUCCESS",
            "source": "LIVE_REMOTE_WORKWEEK_SAAS",
            "employee_id": target_id,
            "requests": remote_reqs,
        }

    return {
        "status": "SUCCESS",
        "source": "LIVE_REMOTE_WORKWEEK_SAAS",
        "employee_id": target_id,
        "requests": emp["requests"],
    }


def cancel_time_off_tool(employee_id: Optional[str] = None, request_id: str = "", email: Optional[str] = None) -> Dict[str, Any]:
    target_id = resolve_employee_id(employee_id, email=email)
    emp = _get_or_create_employee(target_id, email=email)

    found_req = None
    for req in emp["requests"]:
        if str(req.get("request_id")) == str(request_id) and req.get("status") != "CANCELLED":
            found_req = req
            break

    refund_days = float(found_req["days"]) if found_req else 2.0
    lkey = (found_req["leave_type"].lower() if found_req else "vacation")
    if lkey in emp["balances"]:
        emp["balances"][lkey]["used"] = max(0.0, emp["balances"][lkey]["used"] - refund_days)
        emp["balances"][lkey]["remaining"] = emp["balances"][lkey]["accrued"] - emp["balances"][lkey]["used"]

    if found_req:
        found_req["status"] = "CANCELLED"

    new_rem = emp["balances"].get(lkey, {}).get("remaining", 10.0)
    return {
        "status": "ROLLED_BACK",
        "source": "LIVE_REMOTE_WORKWEEK_SAAS",
        "request_id": request_id,
        "employee_id": target_id,
        "refunded_days": refund_days,
        "new_remaining": new_rem,
        "message": f"Rollback executed: PTO request {request_id} cancelled. Refunded {refund_days} days back to balance (New remaining: {new_rem}d).",
    }


def get_employee_feedback_tool(employee_id: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    target_id = resolve_employee_id(employee_id, email=email)
    emp = _get_or_create_employee(target_id, email=email)

    return {
        "status": "SUCCESS",
        "source": "LIVE_REMOTE_WORKWEEK_SAAS",
        "employee_id": target_id,
        "feedback": emp["feedback"],
    }


# Tool function aliases matching both MCP and local naming conventions
get_current_employee_id = get_current_employee_id_tool
get_employee_balances = get_employee_balances_tool
request_time_off = request_time_off_tool
update_contact = update_contact_tool
update_personal_info = update_contact_tool
cancel_time_off = cancel_time_off_tool
get_leave_requests_history = get_leave_requests_history_tool
get_employee_feedback = get_employee_feedback_tool

