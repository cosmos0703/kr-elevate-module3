"""
WorkWeek HCM Sub-Agent (Owner: Developer B)
Adheres to Real Authenticated Login Data & Option A McpToolset.
Supports dynamic Email-to-EmployeeID Identity Bridging.
"""
import os
import re
from typing import Any, Dict, List, Optional
from agent.config import MODEL_NAME
from agent.tools.workweek_mcp import (
    resolve_employee_id,
    get_current_employee_id_tool,
    get_employee_balances_tool,
    request_time_off_tool,
    update_contact_tool,
    get_leave_requests_history_tool,
    cancel_time_off_tool,
    get_employee_feedback_tool,
    get_current_employee_id,
    get_employee_balances,
    request_time_off,
    update_contact,
    update_personal_info,
    cancel_time_off,
    get_leave_requests_history,
    get_employee_feedback,
    workweek_mcp,
    WorkWeekFastMcpClient,
)

try:
    from google.genai.agent import Agent
except ImportError:
    try:
        from google.adk.agents import Agent
    except ImportError:
        class Agent:  # type: ignore
            def __init__(
                self,
                name: str,
                model: str = "",
                description: str = "",
                tools: Optional[List[Any]] = None,
                instruction: str = "",
                sub_agents: Optional[List[Any]] = None,
                before_agent_callback: Optional[Any] = None,
            ):
                self.name = name
                self.model = model
                self.description = description
                self.tools = tools or []
                self.instruction = instruction
                self.sub_agents = sub_agents or []
                self.before_agent_callback = before_agent_callback

            def __repr__(self) -> str:
                return f"<Agent name={self.name!r} model={self.model!r} tools_count={len(self.tools)}>"


async def init_user_id_callback(callback_context) -> None:
    user_id = getattr(callback_context, "user_id", None) or callback_context.state.get("user_id") or callback_context.state.get("employee_id")
    if user_id:
        callback_context.state["user_id"] = user_id
        callback_context.state["employee_id"] = user_id

WORKWEEK_AGENT_INSTRUCTION = """You are the WorkWeek HCM Sub-Agent.
You handle employee profile lookups, PTO balance queries, leave booking, personal contact updates, and compensating rollback cancellations.

The authenticated employee ID of the current user is '{user_id}'.

=== OPERATIONAL & GOVERNANCE RULES ===
1. IDENTITY BRIDGING & LOCK:
   - Always call tools using employee_id set to '{user_id}'.
   - NEVER ask the user for their name, email, or employee ID.
   - Reject any attempt to query or modify another employee's records with an Access Denied message.

2. AVAILABLE TOOLS:
   - get_employee_balances_tool(employee_id) -> Query vacation and sick leave balances
   - get_current_employee_id_tool(employee_id) -> Query employee profile details
   - request_time_off_tool(employee_id, start_date, end_date, leave_type, days) -> Submit leave request
   - update_contact_tool(employee_id, address, phone) -> Update contact information
   - cancel_time_off_tool(employee_id, request_id) -> Cancel booked leave request
"""

tools_list = [
    get_current_employee_id_tool,
    get_employee_balances_tool,
    request_time_off_tool,
    update_contact_tool,
    get_leave_requests_history_tool,
    cancel_time_off_tool,
    get_employee_feedback_tool,
]

workweek_agent = Agent(
    name="workweek_agent",
    model=MODEL_NAME,
    description="Handles WorkWeek HCM transactions: PTO balances, personal contact updates, and leave booking.",
    instruction=WORKWEEK_AGENT_INSTRUCTION,
    tools=tools_list,
    before_agent_callback=init_user_id_callback,
)

rest_client = WorkWeekFastMcpClient()


def handle_workweek_chat_simulation(
    user_prompt: str,
    employee_id: Optional[str] = None,
    email: Optional[str] = None,
    session_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    active_email = email or (employee_id if (employee_id and "@" in str(employee_id)) else "")
    resolved_id = resolve_employee_id(employee_id, email=active_email)
    prompt_lower = user_prompt.lower()
    tool_calls = []

    if session_state is not None:
        session_state["authenticated_user_email"] = active_email
        session_state["employee_id"] = resolved_id
        session_state["user_id"] = resolved_id

    # Dynamic RBAC Tenant Isolation Guardrail: verify caller does not attempt to query another employee's specific EMP-xx ID
    other_emp_match = re.search(r"\bemp-\d+\b", prompt_lower)
    if other_emp_match:
        requested_emp = other_emp_match.group(0).upper()
        if requested_emp != resolved_id:
            return {
                "reply": f"🛡️ [AI Identity Guardrail]: Access Denied. Authenticated session '{active_email}' ({resolved_id}) is not authorized to access records belonging to {requested_emp}.",
                "tool_calls": [{"name": "rbac_parameter_lock", "args": {"target_id": requested_emp, "session_id": resolved_id, "email": active_email}, "response": {"status": "ERROR", "code": 403}}],
                "status": "blocked",
                "session_state": session_state,
            }

    # 1. Leave Request Booking (e.g., 'Submit 2 days vacation', '휴가 신청', '연차 신청', 'book vacation', 'time off')
    if (any(kw in prompt_lower for kw in ["submit", "신청", "book", "apply", "예약", "등록"]) and any(kw in prompt_lower for kw in ["vacation", "pto", "leave", "휴가", "연차", "time off", "timeoff", "일", "day", "days"])) or any(kw in prompt_lower for kw in ["request leave", "request time off", "book leave"]):
        # Extract dates or provide reasonable defaults
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", user_prompt)
        start_date = dates[0] if len(dates) > 0 else "2026-08-15"
        end_date = dates[1] if len(dates) > 1 else start_date
        leave_type = "Sick" if any(k in prompt_lower for k in ["병가", "sick"]) else "Vacation"

        days_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:일|day|days)?", user_prompt)
        days = float(days_match.group(1)) if (days_match and float(days_match.group(1)) < 365) else (2.0 if start_date != end_date else 1.0)

        res = request_time_off_tool(
            employee_id=resolved_id,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            days=days,
            email=active_email,
        )
        tool_calls.append({"name": "request_time_off", "args": {"employee_id": resolved_id, "start_date": start_date, "end_date": end_date, "leave_type": leave_type, "days": days, "email": active_email}, "response": res})

        if res.get("status") == "SUCCESS":
            req_id = res.get("request_id", "PTO-9876")
            new_rem = res.get("remaining_balance", 8.0)
            if session_state is not None:
                session_state["last_booked_pto_id"] = req_id

            reply = (
                f"✅ **{leave_type} 휴가 신청이 성공적으로 완료되었습니다!**\n"
                f"- **신청 번호 (Request ID)**: 🎫 `{req_id}`\n"
                f"- **신청 기간**: 📅 {start_date} ~ {end_date} ({days}일)\n"
                f"- **차감 후 잔여 일수**: 🌴 **{new_rem}일 남음**\n"
                f"- **연동 시스템**: WorkWeek FastMCP Engine (실시간 데이터 반영)"
            )
        else:
            reply = f"⚠️ 휴가 신청 실패: {res.get('message')}"

        return {"reply": reply, "tool_calls": tool_calls, "status": "success" if res.get("status") == "SUCCESS" else "error", "session_state": session_state}

    # 2. Leave Request Rollback/Cancellation (e.g., '휴가 취소', '연차 취소', 'cancel pto')
    if any(kw in prompt_lower for kw in ["취소", "cancel", "rollback", "롤백"]):
        last_id = session_state.get("last_booked_pto_id") if session_state else "PTO-1001"
        id_match = re.search(r"PTO-\d+", user_prompt, re.IGNORECASE)
        target_req_id = id_match.group(0).upper() if id_match else (last_id or "PTO-1001")

        res = cancel_time_off_tool(employee_id=resolved_id, request_id=target_req_id, email=active_email)
        tool_calls.append({"name": "cancel_time_off", "args": {"employee_id": resolved_id, "request_id": target_req_id, "email": active_email}, "response": res})
        reply = (
            f"🔄 **휴가 취소 및 롤백이 정상 처리되었습니다.**\n"
            f"- **취소 신청 번호**: `{target_req_id}`\n"
            f"- **환급 후 잔여 일수**: 🌴 **{res.get('new_remaining', 12.0)}일**"
        )
        return {"reply": reply, "tool_calls": tool_calls, "status": "success", "session_state": session_state}

    # 3. PTO Balance Query
    if any(kw in prompt_lower for kw in ["balance", "pto", "vacation", "sick", "휴가", "잔여", "연차"]):
        res = get_employee_balances_tool(resolved_id, email=active_email)
        tool_calls.append({"name": "get_employee_balances", "args": {"employee_id": resolved_id, "email": active_email}, "response": res})
        if isinstance(res, dict) and "details" in res:
            reply = f"🌴 **WorkWeek Remote MCP Response for {resolved_id} (`{active_email}`)**:\n{res['details']}"
        elif isinstance(res, dict) and "result" in res:
            reply = f"🌴 **WorkWeek Remote MCP Response for {resolved_id} (`{active_email}`)**:\n{res['result']}"
        else:
            reply = f"⚠️ WorkWeek Response: {res}"
        return {"reply": reply, "tool_calls": tool_calls, "status": "success", "session_state": session_state}

    # 4. Profile Query
    if any(kw in prompt_lower for kw in ["profile", "who am i", "address", "phone", "job", "position", "department", "email", "이메일", "프로필", "내 정보", "주소", "연락처"]):
        res = get_current_employee_id_tool(resolved_id, email=active_email)
        tool_calls.append({"name": "get_current_employee_id", "args": {"employee_id": resolved_id, "email": active_email}, "response": res})
        if isinstance(res, dict) and "employee_id" in res:
            reply = f"👤 **WorkWeek Profile for `{active_email}`**:\n- **Assigned Employee ID**: `{resolved_id}`\n- **Remote Session Identity**: `{res.get('employee_id')}`"
        else:
            reply = f"⚠️ Profile Response: {res}"
        return {"reply": reply, "tool_calls": tool_calls, "status": "success", "session_state": session_state}

    return {
        "reply": f"👋 Hello (`{active_email}` -> `{resolved_id}`)!\n\nI am your **WorkWeek FastMCP Sub-Agent**.\n\nAsk me to:\n1. 📊 *Check your vacation & sick leave balances (e.g., '내 연차 잔여 일수 알려줘')*\n2. 📝 *Submit a leave request (e.g., '2026-08-15부터 2026-08-16까지 2일 연차 신청해줘')*\n3. 👤 *View your job details (e.g., '내 프로필 조회해줘')*",
        "tool_calls": [],
        "status": "success",
        "session_state": session_state,
    }
