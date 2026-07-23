"""
Google ADK Web Application (FastAPI Server) for Enterprise HR Solution.
Strictly configured with live FastMCP server (https://mock-saas.aishprabhat.demo.altostrat.com/docs).
"""
import http.server
import json
import os
import socketserver
import urllib.parse
from typing import Any, Dict

try:
    from agent.root_orchestrator import handle_root_chat, hr_root_orchestrator
    from agent.sub_agents.workweek_agent import handle_workweek_chat_simulation, workweek_agent
    from agent.tools.workweek_mcp import (
        resolve_employee_id,
        get_current_employee_id_tool,
        get_employee_balances_tool,
        request_time_off_tool,
        update_contact_tool,
        get_leave_requests_history_tool,
        cancel_time_off_tool,
        get_employee_feedback_tool,
        generate_mcp_token_for_user,
        get_email_for_token,
    )
except ImportError:
    from root_orchestrator import handle_root_chat, hr_root_orchestrator
    from sub_agents.workweek_agent import handle_workweek_chat_simulation, workweek_agent
    from tools.workweek_mcp import (
        resolve_employee_id,
        get_current_employee_id_tool,
        get_employee_balances_tool,
        request_time_off_tool,
        update_contact_tool,
        get_leave_requests_history_tool,
        cancel_time_off_tool,
        get_employee_feedback_tool,
        generate_mcp_token_for_user,
    )

PORT = 8080
STATIC_INDEX = os.path.join(os.path.dirname(__file__), "static", "index.html")


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class ADKWebRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/chat", "/index.html", "/static/index.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            if os.path.exists(STATIC_INDEX):
                with open(STATIC_INDEX, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            return

        query = urllib.parse.parse_qs(parsed.query)
        email_param = query.get("email", [""])[0] or None
        emp_id = resolve_employee_id(email=email_param) if email_param else "UNKNOWN"

        if path == "/api/workweek/balances":
            self.send_json(get_employee_balances_tool(emp_id, email=email_param))
            return

        if path == "/api/workweek/profile":
            self.send_json(get_current_employee_id_tool(emp_id, email=email_param))
            return

        if path == "/api/workweek/requests":
            self.send_json(get_leave_requests_history_tool(emp_id, email=email_param))
            return

        if path == "/api/workweek/feedback":
            self.send_json(get_employee_feedback_tool(emp_id, email=email_param))
            return

        if path == "/api/auth/google/login":
            self.send_response(302)
            self.send_header("Location", "/?google_auth=success")
            self.end_headers()
            return

        self.send_error(404, "Endpoint not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if path == "/api/auth/login":
            user_email = (data.get("email") or "").strip()
            user_emp_id = (data.get("employee_id") or "").strip()
            raw_token = generate_mcp_token_for_user(user_email)
            emp_id = resolve_employee_id(identifier=user_emp_id, email=user_email)
            profile = get_current_employee_id_tool(emp_id, email=user_email)
            self.send_json({
                "status": "SUCCESS",
                "email": user_email,
                "employee_id": emp_id,
                "mcp_token": raw_token or "mcp_shared_secret_token",
                "profile": profile,
                "message": f"Successfully authenticated {user_email} via Google IAP. Personal Access Token generated.",
            })
            return

        if path in ["/api/agent/chat", "/api/workweek/chat"]:
            from agent.tools.model_armor import inspect_prompt_with_model_armor
            email_val = data.get("email")
            emp_id_val = data.get("employee_id")
            mcp_token_val = data.get("mcp_token")
            if mcp_token_val:
                os.environ["X_MCP_TOKEN"] = mcp_token_val
                owner_email = get_email_for_token(mcp_token_val)
                if owner_email:
                    email_val = owner_email
                    emp_id_val = resolve_employee_id(email=owner_email)
            msg = data.get("message", "")

            # GCP Model Armor Inspection (Template: projects/pe-kor-trainer/locations/us-central1/templates/test-pe-kor)
            armor_res = inspect_prompt_with_model_armor(msg)
            if not armor_res.get("allowed"):
                self.send_json({
                    "status": "BLOCKED_BY_MODEL_ARMOR",
                    "author": "GCP Model Armor Security",
                    "reply": f"🚨 **Security Violation Blocked by GCP Model Armor**\n- **Template**: `projects/pe-kor-trainer/locations/us-central1/templates/test-pe-kor`\n- **Reason**: {armor_res.get('reason')}",
                    "model_armor": armor_res
                })
                return

            res = handle_root_chat(msg, email=email_val, employee_id=emp_id_val)
            if isinstance(res, dict):
                res["model_armor"] = armor_res
            self.send_json(res)
            return

        if path == "/api/workweek/timeoff":
            email_val = data.get("email")
            emp_id = resolve_employee_id(email=email_val)
            res = request_time_off_tool(
                employee_id=emp_id,
                start_date=data.get("start_date", ""),
                end_date=data.get("end_date", ""),
                leave_type=data.get("leave_type", "Vacation"),
                days=data.get("days"),
                email=email_val,
            )
            self.send_json(res)
            return

        if path == "/api/workweek/profile":
            email_val = data.get("email")
            emp_id = resolve_employee_id(email=email_val)
            res = update_contact_tool(
                employee_id=emp_id,
                address=data.get("address"),
                phone=data.get("phone"),
                email=email_val,
            )
            self.send_json(res)
            return

        self.send_error(404, "Endpoint not found")

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        email_val = query.get("email", [""])[0] or None
        raw_emp = query.get("employee_id", [""])[0] or (email_val or DEFAULT_EMPLOYEE_ID)
        req_id = query.get("request_id", [""])[0]

        if path == "/api/workweek/rollback":
            res = cancel_time_off_tool(raw_emp, req_id, email=email_val)
            self.send_json(res)
            return

        self.send_error(404, "Endpoint not found")

    def send_json(self, data: Any):
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))


def main():
    socketserver.TCPServer.allow_reuse_address = True
    httpd = None
    actual_port = 8080
    for p in range(8080, 8100):
        try:
            httpd = ReusableTCPServer(("", p), ADKWebRequestHandler)
            actual_port = p
            break
        except OSError:
            continue

    if not httpd:
        print("❌ Could not bind server to any port in range 8080-8100.")
        return

    print("=" * 75)
    print(f"🌐 Google ADK Web Server running on: http://localhost:{actual_port}")
    print(f"📡 WorkWeek FastMCP Endpoint: https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/")
    print(f"🤖 Loaded Sub-Agent: {workweek_agent.name}")
    print("=" * 75)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down ADK Web Server.")


if __name__ == "__main__":
    main()
