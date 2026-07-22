"""
HR Agentic Solution Package (MVP 1)
"""
import sys
import types
import google.adk.agents

# Monkeypatch google.genai.agent to google.adk.agents
genai_agent_module = types.ModuleType("google.genai.agent")
genai_agent_module.Agent = google.adk.agents.Agent
sys.modules["google.genai.agent"] = genai_agent_module

__version__ = "0.1.0"

# Expose agent attribute for ADK CLI evaluation
class MockAgentModule:
    @property
    def root_agent(self):
        from agent.root_orchestrator import hr_root_orchestrator
        return hr_root_orchestrator

agent = MockAgentModule()

# Expose root_agent directly for AgentLoader/dev-server
from agent.root_orchestrator import hr_root_orchestrator as root_agent


