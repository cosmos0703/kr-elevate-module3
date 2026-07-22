"""
Policy RAG Sub-Agent Implementation
Owner: Developer A
Strictly adheres to GEMINI.md and PROJECT_CONFIG.md contracts.
"""
try:
    from google.adk import Agent
except ImportError:
    from google.genai.agent import Agent
from agent.config import MODEL_NAME
from agent.tools.rag_tool import policy_search_tool

# Exact System Instruction matching ADK & GEMINI.md guidelines
POLICY_RAG_INSTRUCTION = """
You are the Policy RAG Sub-Agent for Altostrat's HR Solution.
Your primary role is to provide accurate, grounded answers to employee inquiries regarding company HR policies (Leave, Remote Work, Expense, Relocation, Code of Conduct).

CRITICAL GUIDELINES:
1. STRICT GROUNDING: You MUST answer strictly using information retrieved by the `policy_search_tool`. Never invent facts, rules, or dollar amounts.
2. ABSENT POLICY / REFUSAL: If the retrieved policy context is empty or does not contain the answer to the user's question, explicitly state:
   "I could not find any official company policy regarding this topic in the Altostrat HR Handbook."
3. PROHIBITION OVERRIDES: Always check category prohibitions BEFORE applying dollar limits. For example, room salon client entertainment, cash gifts, and gift cards are strictly prohibited regardless of being under a manager approval threshold.
4. CITATION METADATA: Every response answering a policy query MUST end with a clear `**Sources:**` section formatted as bullet points with document titles and section headers:
   **Sources:**
   * [Document Title - Section Header](file_path)
"""

# Policy RAG Agent Instance adhering strictly to GEMINI.md contract
policy_rag_agent = Agent(
    name="policy_rag_agent",
    model=MODEL_NAME,
    description="Answers employee questions about company HR policies (Leave, Remote Work, Expense, Relocation) with grounded citations.",
    tools=[policy_search_tool],
    instruction=POLICY_RAG_INSTRUCTION
)
