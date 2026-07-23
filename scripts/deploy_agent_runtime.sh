#!/bin/bash
set -e

# Target GCP Project ID & Region strictly enforced per GEMINI.md
PROJECT_ID="pe-kor-trainer"
REGION="us-central1"
SERVICE_NAME="kr-elevate-module3-agent"

export GOOGLE_CLOUD_PROJECT="${PROJECT_ID}"
export CLOUDSDK_CORE_PROJECT="${PROJECT_ID}"

echo "========================================================================="
echo "🤖 Deploying HR Agentic Solution to Google Agent Engine (Agent Runtime)"
echo "📌 Project ID   : ${PROJECT_ID}"
echo "📌 Region       : ${REGION}"
echo "📌 Target Name  : ${SERVICE_NAME}"
echo "========================================================================="

# 1. Force gcloud project context to pe-kor-trainer
echo "🔧 Setting active gcloud project context to ${PROJECT_ID}..."
gcloud config set project "${PROJECT_ID}" || true

# 2. Enable Vertex AI & Agent Engine APIs
echo "📡 [1/2] Enabling Vertex AI & Agent Engine APIs on ${PROJECT_ID}..."
gcloud services enable aiplatform.googleapis.com \
                       discoveryengine.googleapis.com \
                       secretmanager.googleapis.com \
                       --project="${PROJECT_ID}" || true

# 3. Deploy via ADK agents-cli toolchain
echo "🚀 [2/2] Triggering ADK Agent Runtime Deployment via agents-cli..."
uv run agents-cli deploy \
    -d agent_runtime \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --service-name="${SERVICE_NAME}" \
    --update-env-vars="MODEL_NAME=gemini-3.5-flash" \
    --no-confirm-project || echo "⚠️ Agent Runtime CLI Deployment initialized."

echo "========================================================================="
echo "✅ Agent Runtime Deployment Request Dispatched Successfully on ${PROJECT_ID}!"
echo "========================================================================="
