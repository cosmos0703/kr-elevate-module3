"""
Unified Configuration Module (Ref: PROJECT_CONFIG.md)
"""
import os

# GCP Project & Region
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "pe-kor-trainer")
GOOGLE_CLOUD_PROJECT_NUMBER = os.getenv("GOOGLE_CLOUD_PROJECT_NUMBER", "775423734296")
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_REGION", "global")

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

# Google Cloud RAG Configuration (Vertex AI Search / Vertex RAG API / Vector Search)
GCS_KNOWLEDGE_BUCKET = os.getenv("GCS_KNOWLEDGE_BUCKET", "pe-kor-trainer-hr-knowledge")
VERTEX_SEARCH_DATASTORE_ID = os.getenv("VERTEX_SEARCH_DATASTORE_ID", "hr-policy-datastore")
VERTEX_SEARCH_LOCATION = os.getenv("VERTEX_SEARCH_LOCATION", "global")
VERTEX_RAG_CORPUS_ID = os.getenv("VERTEX_RAG_CORPUS_ID", "")
RAG_ENGINE_TYPE = os.getenv("RAG_ENGINE_TYPE", "vertex_search")  # Options: vertex_search | vertex_rag_corpus | vertex_vector_search | local_fallback

# FastMCP Base Endpoints
WORKWEEK_MCP_URL = os.getenv("WORKWEEK_MCP_URL", "https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/")
WORKWEEK_REST_URL = os.getenv("WORKWEEK_REST_URL", "https://mock-saas.aishprabhat.demo.altostrat.com/work-week/api/")
ITSM_MCP_URL = os.getenv("ITSM_MCP_URL", "https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/")

# Performance & Guardrail Limits
MODEL_ARMOR_LATENCY_BUDGET_MS = 300
MAX_RESPONSE_LATENCY_SEC = 10.0
