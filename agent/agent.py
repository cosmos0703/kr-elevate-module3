"""
ADK Agent Entrypoint for agents-cli playground.
Exposes hr_root_orchestrator as root_agent.
"""
from agent.root_orchestrator import hr_root_orchestrator

# Expose hr_root_orchestrator as root_agent so agents-cli playground loads the orchestrator with all 3 sub-agents
root_agent = hr_root_orchestrator
