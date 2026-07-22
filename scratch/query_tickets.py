import asyncio
import os
import sys

sys.path.append(os.getcwd())
os.environ["X_MCP_TOKEN"] = "mcp_j0pahNmjVIKPaehhafM8GetGS2zj6l5YtezknmRDFko"
os.environ["ITSM_MCP_URL"] = "https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/"

from agent.tools.itsm_mcp import list_tickets_tool

async def run():
    print(await list_tickets_tool("EMP-19"))

asyncio.run(run())
