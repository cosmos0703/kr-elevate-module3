#!/usr/bin/env python3
"""
Local Test Runner for policy_rag_agent
Owner: Developer A
"""
import os
import sys

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.sub_agents.policy_rag_agent import policy_rag_agent
from agent.tools.rag_tool import policy_search_tool

def run_test_query(query: str):
    print("=" * 70)
    print(f"❓ USER QUERY: {query}")
    print("=" * 70)
    
    # 1. Test RAG Search Tool output
    tool_output = policy_search_tool(query)
    print(f"🔍 RAG Search Tool Found: {tool_output['found']}")
    print(f"📚 Retrieved Sources Count: {len(tool_output.get('results', []))}")
    for idx, res in enumerate(tool_output.get("results", []), 1):
        print(f"   [{idx}] {res['source']}")
    
    print("\n🤖 AGENT METADATA:")
    print(f"   - Name: {policy_rag_agent.name}")
    print(f"   - Model: {policy_rag_agent.model}")
    print(f"   - Description: {policy_rag_agent.description}")
    print("=" * 70 + "\n")

def main():
    print("🚀 Starting Local Policy RAG Agent Test Runner...")
    
    # Sample Test Queries
    queries = [
        "What is the company policy on paid outpatient sick leave and MC submission deadline?",
        "Can I expense US $80 for a room salon client entertainment night?",
        "What is the policy for pet helicopter transport allowance?" # Hallucination bait
    ]
    
    for q in queries:
        run_test_query(q)

if __name__ == "__main__":
    main()
