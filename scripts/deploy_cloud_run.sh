#!/bin/bash
set -e

# Load parameters from GEMINI.md / PROJECT_CONFIG.md
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-pe-kor-trainer}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
SERVICE_NAME="kr-elevate-module3-web"
IMAGE_URI="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "========================================================================="
echo "🚀 Deploying HR Agentic Solution to Google Cloud Run"
echo "📌 Project ID : ${PROJECT_ID}"
echo "📌 Region     : ${REGION}"
echo "📌 Service    : ${SERVICE_NAME}"
echo "========================================================================="

# 1. Enable required GCP APIs
echo "📡 [1/3] Enabling required Google Cloud APIs..."
gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com \
                       aiplatform.googleapis.com \
                       discoveryengine.googleapis.com \
                       secretmanager.googleapis.com \
                       --project="${PROJECT_ID}" || true

# 2. Build container image via Cloud Build
echo "📦 [2/3] Building container image via Cloud Build..."
gcloud builds submit --tag "${IMAGE_URI}" --project="${PROJECT_ID}" .

# 3. Deploy container image to Cloud Run
echo "🌐 [3/3] Deploying service to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image="${IMAGE_URI}" \
    --platform=managed \
    --region="${REGION}" \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_REGION=${REGION},MODEL_NAME=gemini-3.5-flash" \
    --port=8080 \
    --project="${PROJECT_ID}"

echo "========================================================================="
echo "✅ Cloud Run Deployment Completed Successfully!"
echo "========================================================================="
