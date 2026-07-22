"""
Main Entrypoint Script
"""
from agent.root_orchestrator import hr_root_orchestrator

def main():
    print(f"Loaded Agent: {hr_root_orchestrator.name}")
    print(f"Sub-Agents: {[sa.name for sa in hr_root_orchestrator.sub_agents]}")
    print("HR Agentic Solution initialized successfully.")

if __name__ == "__main__":
    main()
