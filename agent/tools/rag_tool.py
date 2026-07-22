"""
Policy RAG Tool Module (Owner: Developer A)
Provides grounded document search over knowledge/*.md policies.
"""
import glob
import os
import re

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge")


def _chunk_markdown_documents():
    """
    Parses markdown policy files in knowledge/ into structured section chunks.
    """
    chunks = []
    pattern = os.path.join(KNOWLEDGE_DIR, "*.md")
    files = glob.glob(pattern)

    for file_path in files:
        filename = os.path.basename(file_path)
        if filename.startswith("README"):
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split content by sections (## Heading)
        sections = re.split(r"\n(?=##\s+)", content)
        doc_title = sections[0].split("\n")[0].replace("#", "").strip() if sections else filename

        for sec in sections:
            lines = sec.strip().split("\n")
            if not lines:
                continue
            section_title = lines[0].replace("#", "").strip()
            body = "\n".join(lines[1:]).strip()

            chunks.append({
                "doc_name": filename,
                "doc_title": doc_title,
                "section_title": section_title,
                "content": body,
                "full_text": f"{doc_title} - {section_title}: {body}",
                "file_path": os.path.abspath(file_path),
            })

    return chunks


def policy_search_tool(query: str) -> dict:
    """
    Searches the corporate HR policy knowledge base for relevant sections.

    Args:
        query (str): Search query or user question regarding company policies.

    Returns:
        dict: Grounded search result containing:
            - found (bool): True if matching policy chunks were retrieved.
            - chunks (list): List of matching section snippets and citations.
            - citations (list): Clickable citation metadata.
            - message (str): Explanation if no policy was found.
    """
    chunks = _chunk_markdown_documents()
    query_tokens = set(re.findall(r"\w+", query.lower()))

    # Score chunks by keyword token intersection & relevance
    scored_chunks = []
    for chunk in chunks:
        chunk_tokens = set(re.findall(r"\w+", chunk["full_text"].lower()))
        overlap = query_tokens.intersection(chunk_tokens)
        score = len(overlap)

        # Boost score for key domain terms
        for token in query_tokens:
            if token in chunk["section_title"].lower():
                score += 3
            if token in chunk["content"].lower():
                score += 1

        if score > 1:  # Relevance threshold
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    if not scored_chunks:
        return {
            "found": False,
            "message": f"No official company policy found for query: '{query}'.",
            "chunks": [],
            "citations": []
        }

    # Return top matching chunks (up to 3)
    top_chunks = [item[1] for item in scored_chunks[:3]]
    citations = [
        {
            "doc_name": chunk["doc_name"],
            "section_title": chunk["section_title"],
            "file_path": chunk["file_path"],
            "citation_str": f"[{chunk['doc_name']} - {chunk['section_title']}](file://{chunk['file_path']})"
        }
        for chunk in top_chunks
    ]

    return {
        "found": True,
        "query": query,
        "snippets": [f"### {c['section_title']}\n{c['content']}" for c in top_chunks],
        "citations": citations
    }
