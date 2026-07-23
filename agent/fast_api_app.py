"""
Google ADK Web Application (FastAPI Server) for WorkWeek Sub-Agent.
Strictly configured with live FastMCP server (https://mock-saas.aishprabhat.demo.altostrat.com/docs).
"""
import http.server
import json
import os
import socketserver
import urllib.parse
from typing import Any, Dict

from agent.root_orchestrator import handle_root_chat, hr_root_orchestrator
from agent.sub_agents.workweek_agent import handle_workweek_chat_simulation, workweek_agent
from agent.tools.workweek_mcp import (
    DEFAULT_EMPLOYEE_ID,
    DEFAULT_USER_EMAIL,
    resolve_employee_id,
    get_current_employee_id_tool,
    get_employee_balances_tool,
    request_time_off_tool,
    update_contact_tool,
    get_leave_requests_history_tool,
    cancel_time_off_tool,
    get_employee_feedback_tool,
)

PORT = 8080
STATIC_INDEX = os.path.join(os.path.dirname(__file__), "static", "index.html")


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class ADKWebRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        email_param = query.get("email", [""])[0] or None
        raw_emp = query.get("employee_id", [""])[0] or (email_param or DEFAULT_EMPLOYEE_ID)
        emp_id = resolve_employee_id(raw_emp, email=email_param)

        if path in ["/", "/chat", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            if os.path.exists(STATIC_INDEX):
                with open(STATIC_INDEX, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            return

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

        if path in ["/api/agent/chat", "/api/workweek/chat"]:
            email_val = data.get("email")
            raw_emp = data.get("employee_id") or (email_val or DEFAULT_EMPLOYEE_ID)
            msg = data.get("message", "")
            res = handle_root_chat(msg, email=email_val, employee_id=raw_emp)
            self.send_json(res)
            return

        if path == "/api/workweek/timeoff":
            email_val = data.get("email")
            raw_emp = data.get("employee_id") or (email_val or DEFAULT_EMPLOYEE_ID)
            res = request_time_off_tool(
                employee_id=raw_emp,
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
            raw_emp = data.get("employee_id") or (email_val or DEFAULT_EMPLOYEE_ID)
            res = update_contact_tool(
                employee_id=raw_emp,
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
    try:
        httpd = ReusableTCPServer(("", PORT), ADKWebRequestHandler)
    except OSError:
        # Fallback to next open port if 8080 is momentarily held
        httpd = ReusableTCPServer(("", 8081), ADKWebRequestHandler)

    actual_port = httpd.server_address[1]
    print("=" * 75)
    print(f"🌐 Google ADK Web Server running on: http://localhost:{actual_port}")
    print(f"📡 WorkWeek FastMCP Endpoint: https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/")
    print(f"🤖 Loaded Sub-Agent: {workweek_agent.name} (EMP-26: Inhyep Employee)")
    print("=" * 75)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down ADK Web Server.")


if __name__ == "__main__":
    main()
