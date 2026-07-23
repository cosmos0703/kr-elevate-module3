"""
Main Entrypoint Script for HR Agentic Solution (MVP 1)
"""
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.root_orchestrator import hr_root_orchestrator

def main():
    print("=" * 60)
    print(f"🤖 Loaded Root Orchestrator: {hr_root_orchestrator.name}")
    print(f"📌 Model: {hr_root_orchestrator.model}")
    print("=" * 60)
    print("🔗 Registered Sub-Agents:")
    for sub in hr_root_orchestrator.sub_agents:
        print(f"  - [{sub.name}]: {sub.description[:70]}...")
    print("=" * 60)
    print("✅ HR Multi-Agent System (MVP 1) initialized and ready.")

if __name__ == "__main__":
    main()
