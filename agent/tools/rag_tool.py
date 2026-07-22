"""
Policy RAG Tool for Policy Search and Grounded Citation Generation
Delegates to GoogleCloudRAGEngine (Vertex AI Search, Vertex RAG Corpus, Vector Search, Local Fallback)
Owner: Developer A
Branch: dulee
"""
from typing import Any, Dict

from agent.tools.gcp_rag_engine import GoogleCloudRAGEngine

# Global RAG Engine Instance
_rag_engine = GoogleCloudRAGEngine()


def policy_search_tool(query: str) -> Dict[str, Any]:
    """
    Searches the official Altostrat HR Policy Handbook for governing rules, spend limits,
    prohibitions, leave entitlements, and compliance guidelines.

    Args:
        query: The natural language policy inquiry or topic to search.

    Returns:
        Dictionary containing matching policy sections, content snippets, and verified source citations.
        Strict Contract Preserved:
        {
            "found": bool,
            "query": str,
            "results": [{"source": str, "content": str}, ...],
            "citations": [{"document": str, "section": str, "file": str}, ...]
        }
    """
    raw_results = _rag_engine.search(query, top_k=4)

    if not raw_results:
        return {
            "found": False,
            "query": query,
            "message": "No matching policy sections found in the handbook.",
            "results": [],
            "citations": [],
        }

    formatted_results = []
    citations = []

    for r in raw_results:
        doc_title = r.get("doc_title", "HR Policy")
        header = r.get("header", "General Guidelines")
        file_path = r.get("file_path", "")
        content = r.get("content", "")

        citation = {
            "document": doc_title,
            "section": header,
            "file": file_path,
        }
        citations.append(citation)
        formatted_results.append({
            "source": f"{doc_title} - {header} ({file_path})",
            "content": content,
        })

    return {
        "found": True,
        "query": query,
        "results": formatted_results,
        "citations": citations,
    }
