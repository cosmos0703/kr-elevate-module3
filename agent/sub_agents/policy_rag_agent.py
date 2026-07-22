"""
Policy RAG Sub-Agent (Owner: Developer A)
"""
from google.genai.agent import Agent
from agent.config import MODEL_NAME
from agent.tools.rag_tool import policy_search_tool

policy_rag_agent = Agent(
    name="policy_rag_agent",
    model=MODEL_NAME,
    description="Answers employee questions about company HR policies (Leave, Remote Work, Expense, Relocation) with grounded citations.",
    tools=[policy_search_tool],
    instruction="Search HR policy vector database and return grounded answers with verified citation links."
)
