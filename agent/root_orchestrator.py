"""
Root Orchestrator Agent Stub
TODO: Assemble 3 sub-agents and complete cross-system routing & compensating transaction rollback rules.
"""
try:
    from google.adk import Agent
except ImportError:
    from google.genai.agent import Agent
from agent.config import MODEL_NAME
from agent.sub_agents import policy_rag_agent, workweek_agent, itsm_agent

# Root Orchestrator Agent (TODO: Finalize routing instructions after sub-agents are developed)
hr_root_orchestrator = Agent(
    name="hr_root_orchestrator",
    model=MODEL_NAME,
    description="Main HR Orchestrator routing user intents and executing cross-system multi-step workflows.",
    sub_agents=[
        policy_rag_agent,       # Developer A
        workweek_agent,         # Developer B
        itsm_agent,             # Developer C
    ],
    instruction="""
    TODO: Fill in multi-turn intent routing and compensating transaction rollback logic here.
    - UC-1.1 ~ UC-1.3: Delegate directly to sub-agents based on intent.
    - UC-2.1 ~ UC-2.3: Execute cross-system steps in sequence and rollback on failure.
    """
)
