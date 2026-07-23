"""
Main Entrypoint Script for HR Agentic Solution (Terminal CLI & ADK Web Server).
Supports interactive terminal conversation with email-to-agent delegation.
"""
import argparse
import os
import sys

# Ensure repository root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.root_orchestrator import handle_root_chat, hr_root_orchestrator
from agent.tools.workweek_mcp import (
    DEFAULT_EMPLOYEE_ID,
    DEFAULT_USER_EMAIL,
    resolve_employee_id,
    get_current_employee_id_tool,
    get_employee_balances_tool,
)


def run_terminal_chat(initial_email: str = DEFAULT_USER_EMAIL, initial_emp_id: str = DEFAULT_EMPLOYEE_ID):
    current_email = initial_email or DEFAULT_USER_EMAIL
    current_emp_id = resolve_employee_id(initial_emp_id, email=current_email)
    session_state = {}

    print("=" * 75)
    print("🤖 HR Multi-Agent & WorkWeek Sub-Agent Interactive Terminal CLI")
    print(f"📧 Active Email       : {current_email}")
    print(f"🆔 Bound Employee ID  : {current_emp_id}")
    print("📡 FastMCP Endpoint   : https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/")
    print("=" * 75)

    p = get_current_employee_id_tool(current_emp_id, email=current_email)
    b = get_employee_balances_tool(current_emp_id, email=current_email)
    vac = b.get("balances", {}).get("vacation", {})
    sick = b.get("balances", {}).get("sick", {})

    print(f"✅ [Live Profile]  Name: {p.get('name')} | Job: {p.get('job_title')} | Dept: {p.get('department')}")
    print(f"🌴 [Live Balances] Vacation: {vac.get('remaining', 12.0)}d left | Sick: {sick.get('remaining', 10.0)}d left")
    print("-" * 75)
    print("💡 Commands & Usage:")
    print("   - Type your questions (e.g. '내 연차 잔여 일수 알려줘', '내 프로필 조회해줘')")
    print("   - Type '/email <new_email>' to switch email session (e.g. '/email inhyep@gcp.altostrat.com')")
    print("   - Type 'exit' or 'quit' to exit terminal")
    print("=" * 75)

    while True:
        try:
            prompt = input(f"\n💬 [{current_email} ({current_emp_id})] You > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting terminal CLI. Goodbye!")
            break

        if not prompt:
            continue

        if prompt.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break

        if prompt.startswith("/email ") or prompt.startswith("/user "):
            parts = prompt.split()
            if len(parts) > 1:
                current_email = parts[1].strip()
                current_emp_id = resolve_employee_id(current_email, email=current_email)
                print(f"🔄 Switched active email session to: {current_email} ({current_emp_id})")
                b = get_employee_balances_tool(current_emp_id, email=current_email)
                vac = b.get("balances", {}).get("vacation", {})
                print(f"🌴 Updated Balances -> Vacation: {vac.get('remaining', 12.0)}d left")
            continue

        res = handle_root_chat(
            user_prompt=prompt,
            email=current_email,
            employee_id=current_emp_id,
            session_state=session_state,
        )

        reply = res.get("reply", "")
        status = res.get("status", "success")
        status_icon = "🛡️" if status == "blocked" else "🤖"

        print(f"\n{status_icon} Agent > {reply}")


def main():
    parser = argparse.ArgumentParser(description="HR Agentic Solution CLI & Web Server")
    parser.add_argument("--web", "-w", action="store_true", help="Launch FastAPI web server")
    parser.add_argument("--email", "-e", type=str, default=DEFAULT_USER_EMAIL, help="User email address")
    parser.add_argument("--id", "-i", type=str, default=DEFAULT_EMPLOYEE_ID, help="Employee ID")

    args, unknown = parser.parse_known_args()

    if args.web or "--web" in sys.argv or "-w" in sys.argv:
        from agent.fast_api_app import main as start_web
        start_web()
        return

    run_terminal_chat(initial_email=args.email, initial_emp_id=args.id)


if __name__ == "__main__":
    main()

