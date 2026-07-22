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

# FastMCP Base Endpoints
WORKWEEK_MCP_URL = os.getenv("WORKWEEK_MCP_URL", "http://localhost:8001/work-week/mcp/")
WORKWEEK_REST_URL = os.getenv("WORKWEEK_REST_URL", "http://localhost:8001/work-week/api/")
ITSM_MCP_URL = os.getenv("ITSM_MCP_URL", "http://localhost:8002/service-immediately/mcp/")

# Performance & Guardrail Limits
MODEL_ARMOR_LATENCY_BUDGET_MS = 300
MAX_RESPONSE_LATENCY_SEC = 10.0
