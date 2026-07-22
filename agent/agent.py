"""
ADK Agent Entrypoint for agents-cli playground.
Allows testing individual sub-agents or the root HR orchestrator locally in agents-cli playground.

To select active agent in agents-cli playground:
  - ACTIVE_AGENT=root        agents-cli playground --port 8088
  - ACTIVE_AGENT=policy_rag  agents-cli playground --port 8088
  - ACTIVE_AGENT=workweek    agents-cli playground --port 8088
  - ACTIVE_AGENT=itsm        agents-cli playground --port 8088
"""
import os
from agent.sub_agents.policy_rag_agent import policy_rag_agent
from agent.sub_agents.workweek_agent import workweek_agent
from agent.sub_agents.itsm_agent import itsm_agent
from agent.root_orchestrator import hr_root_orchestrator

ACTIVE_AGENT_NAME = os.getenv("ACTIVE_AGENT", "root").strip().lower()

if ACTIVE_AGENT_NAME in ["policy_rag", "policy"]:
    root_agent = policy_rag_agent
elif ACTIVE_AGENT_NAME in ["workweek", "hcm"]:
    root_agent = workweek_agent
elif ACTIVE_AGENT_NAME in ["itsm", "service_immediately"]:
    root_agent = itsm_agent
else:
    root_agent = hr_root_orchestrator
