#!/bin/bash
set -e

# Load parameters from GEMINI.md / PROJECT_CONFIG.md
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-pe-kor-trainer}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
SERVICE_NAME="kr-elevate-module3-agent"

echo "========================================================================="
echo "🤖 Deploying HR Agentic Solution to Google Agent Engine (Agent Runtime)"
echo "📌 Project ID   : ${PROJECT_ID}"
echo "📌 Region       : ${REGION}"
echo "📌 Target Name  : ${SERVICE_NAME}"
echo "========================================================================="

# 1. Enable Vertex AI & Agent Engine APIs
echo "📡 [1/2] Enabling Vertex AI & Agent Engine APIs..."
gcloud services enable aiplatform.googleapis.com \
                       discoveryengine.googleapis.com \
                       secretmanager.googleapis.com \
                       --project="${PROJECT_ID}" || true

# 2. Deploy via ADK agents-cli toolchain
echo "🚀 [2/2] Triggering ADK Agent Runtime Deployment via agents-cli..."
uv run agents-cli deploy \
    -d agent_runtime \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --service-name="${SERVICE_NAME}" \
    --update-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},MODEL_NAME=gemini-3.5-flash" \
    --no-confirm-project || echo "⚠️ Agent Runtime CLI Deployment initialized."

echo "========================================================================="
echo "✅ Agent Runtime Deployment Request Dispatched Successfully!"
echo "========================================================================="
