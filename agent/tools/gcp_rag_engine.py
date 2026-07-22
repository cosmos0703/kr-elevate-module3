"""
Google Cloud RAG Engine Implementation
Provides multi-engine retrieval (Vertex AI Search, Vertex RAG Corpus, Vertex Vector Search, Local Fallback)
Owner: Developer A
Branch: dulee
"""
import glob
import logging
import os
import re
from typing import Any, Dict, List, Optional

from agent.config import (
    GCS_KNOWLEDGE_BUCKET,
    GOOGLE_CLOUD_PROJECT,
    RAG_ENGINE_TYPE,
    VERTEX_RAG_CORPUS_ID,
    VERTEX_SEARCH_DATASTORE_ID,
    VERTEX_SEARCH_LOCATION,
)

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../knowledge"))


class PolicyIndex:
    """Indexed storage and retrieval system for HR Policy markdown documents."""

    def __init__(self, knowledge_dir: Optional[str] = None):
        self.knowledge_dir = knowledge_dir or KNOWLEDGE_DIR
        self.documents: List[Dict[str, Any]] = []
        self._load_documents()

    def _load_documents(self):
        """Loads and chunks markdown policy files accurately."""
        pattern = os.path.join(self.knowledge_dir, "**/*.md")
        filepaths = glob.glob(pattern, recursive=True)

        for path in filepaths:
            if os.path.basename(path) == "README.md":
                continue

            rel_path = os.path.relpath(path, self.knowledge_dir).replace("\\", "/")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            sections = re.split(r"\n(?=#{1,3}\s)", content)
            doc_title = os.path.basename(path).replace(".md", "").replace("-", " ").title()

            for section in sections:
                lines = section.strip().split("\n")
                if not lines or not lines[0]:
                    continue

                if lines[0].startswith("#"):
                    header = lines[0].lstrip("#").strip()
                    section_text = "\n".join(lines[1:]).strip() if len(lines) > 1 else lines[0]
                else:
                    header = "General Guidelines"
                    section_text = "\n".join(lines).strip()

                if len(section_text.strip()) > 30:
                    self.documents.append({
                        "file_path": rel_path,
                        "doc_title": doc_title,
                        "header": header,
                        "content": section_text.strip(),
                        "full_text": f"{doc_title} > {header}\n{section_text.strip()}"
                    })

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Performs term relevance scoring supporting short acronyms and word boundary matching."""
        # Include 2-character terms (e.g. HR, IT, PTO)
        query_terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) >= 2]
        scored_results = []

        for doc in self.documents:
            text_lower = doc["full_text"].lower()
            score = 0
            for term in query_terms:
                # Exact word boundary matching to avoid partial substring false positives
                matches = len(re.findall(rf"\b{re.escape(term)}\b", text_lower))
                if matches > 0:
                    score += matches
                    if re.search(rf"\b{re.escape(term)}\b", doc["doc_title"].lower()):
                        score += 5
                    if re.search(rf"\b{re.escape(term)}\b", doc["header"].lower()):
                        score += 3

            if score > 0:
                doc_copy = dict(doc)
                doc_copy["score"] = float(score)
                scored_results.append((score, doc_copy))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_results[:top_k]]


class GoogleCloudRAGEngine:
    """
    Unified Google Cloud RAG Engine abstraction supporting Vertex AI Search (Discovery Engine),
    Vertex AI RAG Corpus, Vertex Vector Search, and local markdown index fallback.
    """

    def __init__(
        self,
        engine_type: Optional[str] = None,
        project_id: Optional[str] = None,
        datastore_id: Optional[str] = None,
        location: Optional[str] = None,
        rag_corpus_id: Optional[str] = None,
        knowledge_dir: Optional[str] = None,
    ):
        self.engine_type = engine_type or RAG_ENGINE_TYPE
        self.project_id = project_id or GOOGLE_CLOUD_PROJECT
        self.datastore_id = datastore_id or VERTEX_SEARCH_DATASTORE_ID
        self.location = location or VERTEX_SEARCH_LOCATION
        self.rag_corpus_id = rag_corpus_id or VERTEX_RAG_CORPUS_ID
        self.local_index = PolicyIndex(knowledge_dir=knowledge_dir)

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Dispatches search query based on self.engine_type and returns standardized results.

        Standard item dictionary format:
        {
            "doc_title": str,
            "header": str,
            "file_path": str,
            "content": str,
            "full_text": str,
            "score": float
        }
        """
        if self.engine_type == "vertex_search":
            results = self._search_vertex_search(query, top_k)
            if results:
                return results
        elif self.engine_type == "vertex_rag_corpus":
            results = self._search_vertex_rag_corpus(query, top_k)
            if results:
                return results
        elif self.engine_type == "vertex_vector_search":
            results = self._search_vertex_vector_search(query, top_k)
            if results:
                return results

        # Fallback to local index if engine_type is "local_fallback" or GCP retrieval returned empty/failed
        return self._search_local_fallback(query, top_k)

    def _search_vertex_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search using Google Cloud Discovery Engine (Vertex AI Search)."""
        try:
            from google.cloud import discoveryengine_v1 as discoveryengine

            client_options = None
            if self.location != "global":
                client_options = {"api_endpoint": f"{self.location}-discoveryengine.googleapis.com"}

            client = discoveryengine.SearchServiceClient(client_options=client_options)
            serving_config = client.serving_config_path(
                project=self.project_id,
                location=self.location,
                data_store=self.datastore_id,
                serving_config="default_config",
            )
            request = discoveryengine.SearchRequest(
                serving_config=serving_config,
                query=query,
                page_size=top_k,
            )
            response = client.search(request)
            results = []
            for rank, result in enumerate(response.results):
                data = result.document.derived_struct_data or {}
                title = data.get("title") or f"Policy Document {rank + 1}"
                snippets = data.get("snippets") or []
                snippet_text = snippets[0].get("snippet", "") if snippets else ""
                if not snippet_text:
                    snippet_text = data.get("link", "") or str(data)

                uri = data.get("link") or result.document.name or "GCP Vertex Search"
                results.append({
                    "doc_title": str(title),
                    "header": "Policy Guidelines",
                    "file_path": str(uri),
                    "content": str(snippet_text),
                    "full_text": f"{title} > Policy Guidelines\n{snippet_text}",
                    "score": float(1.0 - (rank * 0.1)),
                })
            return results
        except Exception as e:
            logger.warning(f"Vertex Search API call failed: {e}. Falling back to local index.")
            return []

    def _search_vertex_rag_corpus(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search using Vertex AI RAG API (vertexai.preview.rag)."""
        if not self.rag_corpus_id:
            logger.info("VERTEX_RAG_CORPUS_ID is empty. Falling back to local index.")
            return []

        try:
            import vertexai
            from vertexai.preview import rag

            loc = self.location if self.location != "global" else os.getenv("GOOGLE_CLOUD_REGION_RAG", "us-central1")
            vertexai.init(project=self.project_id, location=loc)

            rag_resources = [rag.RagResource(rag_corpus=self.rag_corpus_id)]

            response = rag.retrieval_query(
                rag_resources=rag_resources,
                text=query,
                similarity_top_k=top_k,
            )
            results = []
            contexts = getattr(response, "contexts", None)
            context_list = getattr(contexts, "contexts", []) if contexts else []

            for rank, ctx in enumerate(context_list):
                doc_title = getattr(ctx, "source_display_name", None) or f"RAG Doc {rank + 1}"
                content_text = getattr(ctx, "text", "") or ""
                uri = getattr(ctx, "source_uri", None) or "Vertex RAG Corpus"
                score = getattr(ctx, "score", None)
                score_val = float(score) if score is not None else float(1.0 - (rank * 0.1))

                results.append({
                    "doc_title": str(doc_title),
                    "header": "RAG Corpus Section",
                    "file_path": str(uri),
                    "content": str(content_text),
                    "full_text": f"{doc_title} > RAG Corpus Section\n{content_text}",
                    "score": score_val,
                })
            return results
        except Exception as e:
            logger.warning(f"Vertex RAG Corpus search failed: {e}. Falling back to local index.")
            return []

    def _search_vertex_vector_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search using Vertex Vector Search matching engine."""
        endpoint_id = os.getenv("VERTEX_VECTOR_SEARCH_ENDPOINT_ID", "")
        if not endpoint_id:
            logger.info("VERTEX_VECTOR_SEARCH_ENDPOINT_ID not set. Falling back to local index.")
            return []

        try:
            from google.cloud import aiplatform
            import vertexai
            from vertexai.language_models import TextEmbeddingModel

            loc = self.location if self.location != "global" else os.getenv("GOOGLE_CLOUD_REGION_RAG", "us-central1")
            vertexai.init(project=self.project_id, location=loc)

            model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            embeddings = model.get_embeddings([query])
            query_vector = embeddings[0].values

            endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=endpoint_id)
            response = endpoint.find_neighbors(
                deployed_index_id=os.getenv("DEPLOYED_INDEX_ID", "policy_index"),
                queries=[query_vector],
                num_neighbors=top_k,
            )
            results = []
            if response and len(response) > 0:
                for rank, match in enumerate(response[0]):
                    doc_id = match.id
                    score_val = float(match.distance) if hasattr(match, "distance") else float(1.0 - (rank * 0.1))
                    results.append({
                        "doc_title": f"Vector Search Doc {doc_id}",
                        "header": "Vector Search Result",
                        "file_path": f"vector_search://{doc_id}",
                        "content": f"Matching vector document ID {doc_id}",
                        "full_text": f"Vector Search Doc {doc_id} > Vector Search Result",
                        "score": score_val,
                    })
            return results
        except Exception as e:
            logger.warning(f"Vertex Vector Search failed: {e}. Falling back to local index.")
            return []

    def _search_local_fallback(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback keyword and semantic search using local PolicyIndex."""
        results = self.local_index.search(query, top_k=top_k)
        standardized = []
        for idx, item in enumerate(results):
            std_item = dict(item)
            if "score" not in std_item:
                std_item["score"] = float(1.0 - (idx * 0.1))
            standardized.append(std_item)
        return standardized
