"""
ADK Agent Entrypoint for agents-cli playground.
Allows testing individual sub-agents locally in agents-cli playground.

To select which sub-agent to test in agents-cli playground:
  - ACTIVE_AGENT=policy_rag agents-cli playground --port 8088
  - ACTIVE_AGENT=workweek   agents-cli playground --port 8088
  - ACTIVE_AGENT=itsm       agents-cli playground --port 8088
"""
import os
from agent.sub_agents.policy_rag_agent import policy_rag_agent
from agent.sub_agents.workweek_agent import workweek_agent
from agent.sub_agents.itsm_agent import itsm_agent

ACTIVE_AGENT_NAME = os.getenv("ACTIVE_AGENT", "policy_rag").strip().lower()

if ACTIVE_AGENT_NAME in ["workweek", "workweek_agent", "hcm"]:
    root_agent = workweek_agent
elif ACTIVE_AGENT_NAME in ["itsm", "service_immediately", "service_immediately_agent"]:
    root_agent = itsm_agent
else:
    root_agent = policy_rag_agent
