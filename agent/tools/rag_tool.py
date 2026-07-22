"""
Policy RAG Tool for Policy Search and Grounded Citation Generation
Owner: Developer A
"""
import glob
import os
import re
from typing import List, Dict, Any

# Path to policy documents
KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../knowledge"))


class PolicyIndex:
    """Indexed storage and retrieval system for HR Policy markdown documents."""
    
    def __init__(self, knowledge_dir: str = KNOWLEDGE_DIR):
        self.knowledge_dir = knowledge_dir
        self.documents: List[Dict[str, Any]] = []
        self._load_documents()

    def _load_documents(self):
        """Loads and chunks markdown policy files."""
        pattern = os.path.join(self.knowledge_dir, "**/*.md")
        filepaths = glob.glob(pattern, recursive=True)
        
        for path in filepaths:
            if os.path.basename(path) == "README.md":
                continue
            
            rel_path = os.path.relpath(path, self.knowledge_dir)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split document by headers (# or ## or ###) into sections
            sections = re.split(r'\n(?=#{1,3}\s)', content)
            doc_title = os.path.basename(path).replace(".md", "").replace("-", " ").title()
            
            for section in sections:
                lines = section.strip().split("\n")
                if not lines or not lines[0]:
                    continue
                
                header = lines[0].lstrip("#").strip() if lines[0].startswith("#") else "General Guidelines"
                section_text = "\n".join(lines[1:]) if len(lines) > 1 else lines[0]
                
                if len(section_text.strip()) > 30:
                    self.documents.append({
                        "file_path": rel_path,
                        "doc_title": doc_title,
                        "header": header,
                        "content": section_text.strip(),
                        "full_text": f"{doc_title} > {header}\n{section_text.strip()}"
                    })

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Performs keyword and semantic relevance scoring over policy chunks.
        """
        query_terms = [t.lower() for t in re.findall(r'\w+', query) if len(t) > 2]
        scored_results = []
        
        for doc in self.documents:
            text_lower = doc["full_text"].lower()
            score = 0
            for term in query_terms:
                if term in text_lower:
                    # Count frequency and give extra weight to title/header matches
                    score += text_lower.count(term)
                    if term in doc["doc_title"].lower():
                        score += 5
                    if term in doc["header"].lower():
                        score += 3
            
            if score > 0:
                scored_results.append((score, doc))
        
        # Sort by relevance score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_results[:top_k]]


# Instantiate global index
_policy_index = PolicyIndex()


def policy_search_tool(query: str) -> Dict[str, Any]:
    """
    Searches the official Altostrat HR Policy Handbook for governing rules, spend limits,
    prohibitions, leave entitlements, and compliance guidelines.

    Args:
        query: The natural language policy inquiry or topic to search.

    Returns:
        Dictionary containing matching policy sections, content snippets, and verified source citations.
    """
    results = _policy_index.search(query, top_k=4)
    
    if not results:
        return {
            "found": False,
            "query": query,
            "message": "No matching policy sections found in the handbook.",
            "results": []
        }
    
    formatted_results = []
    citations = []
    
    for r in results:
        citation = {
            "document": r["doc_title"],
            "section": r["header"],
            "file": r["file_path"]
        }
        citations.append(citation)
        formatted_results.append({
            "source": f"{r['doc_title']} - {r['header']} ({r['file_path']})",
            "content": r["content"]
        })
        
    return {
        "found": True,
        "query": query,
        "results": formatted_results,
        "citations": citations
    }
