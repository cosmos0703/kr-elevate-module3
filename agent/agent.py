"""
ADK Agent Entrypoint for agents-cli playground.
Exposes policy_rag_agent as root_agent for testing.
"""
from agent.sub_agents.policy_rag_agent import policy_rag_agent

# Expose policy_rag_agent as root_agent so agents-cli playground loads it directly
root_agent = policy_rag_agent
