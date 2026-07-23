import asyncio
import os
import sys

# Add current workspace to path
sys.path.append(os.getcwd())

# Force environment variables for the project
os.environ["GOOGLE_CLOUD_PROJECT"] = "pe-kor-trainer"
os.environ["GOOGLE_CLOUD_PROJECT_NUMBER"] = "775423734296"
os.environ["GOOGLE_CLOUD_REGION"] = "global"
os.environ["MODEL_NAME"] = "gemini-3.5-flash"
os.environ["X_MCP_TOKEN"] = "mcp_j0pahNmjVIKPaehhafM8GetGS2zj6l5YtezknmRDFko"
os.environ["ITSM_MCP_URL"] = "https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/"

# Monkeypatch itsm_mcp tools for local evaluation
import agent.tools.itsm_mcp

async def list_tickets_tool(requested_by: str) -> list:
    print(f"[MOCK] list_tickets_tool called with requested_by={requested_by}")
    return [
        {
            "ticket_id": "INC-54321",
            "requested_by": requested_by,
            "category": "IT Support",
            "short_description": "VPN connection ticket",
            "status": "In Progress",
            "priority": "3 - Moderate"
        }
    ]

agent.tools.itsm_mcp.list_tickets_tool = list_tickets_tool
print(f"DEBUG: run_local_eval.py monkeypatched list_tickets_tool = {list_tickets_tool}", flush=True)
print(f"DEBUG: run_local_eval.py module list_tickets_tool = {agent.tools.itsm_mcp.list_tickets_tool}", flush=True)

from google.adk.evaluation.agent_evaluator import AgentEvaluator

# Directly monkeypatch the itsm_agent's tool list since imports are already resolved
from agent.sub_agents.itsm_agent import itsm_agent
for i, tool in enumerate(itsm_agent.tools):
    if getattr(tool, "__name__", "") == "list_tickets_tool":
        itsm_agent.tools[i] = list_tickets_tool
        print(f"DEBUG: Successfully monkeypatched list_tickets_tool inside itsm_agent.tools list!", flush=True)

async def main():
    try:
        await AgentEvaluator.evaluate(
            agent_module="agent",
            agent_name="service_immediately_agent",
            eval_dataset_file_path_or_dir="evals/datasets/test.evalset.json",
            num_runs=1,
            print_detailed_results=True
        )
        print("Evaluation finished successfully!")
    except Exception as e:
        print(f"Evaluation failed with error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
