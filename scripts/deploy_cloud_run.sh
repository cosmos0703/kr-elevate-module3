#!/bin/bash
set -e

# Target GCP Project ID & Region strictly enforced per GEMINI.md
PROJECT_ID="pe-kor-trainer"
REGION="us-central1"
SERVICE_NAME="kr-elevate-module3-web"
IMAGE_URI="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "========================================================================="
echo "🚀 Deploying HR Agentic Solution to Google Cloud Run"
echo "📌 Project ID : ${PROJECT_ID}"
echo "📌 Region     : ${REGION}"
echo "📌 Service    : ${SERVICE_NAME}"
echo "========================================================================="

# 1. Enable required GCP APIs
echo "📡 [1/3] Enabling required Google Cloud APIs for project ${PROJECT_ID}..."
gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com \
                       aiplatform.googleapis.com \
                       discoveryengine.googleapis.com \
                       secretmanager.googleapis.com \
                       --project="${PROJECT_ID}" || true

# 2. Build container image via Cloud Build
echo "📦 [2/3] Building container image via Cloud Build on ${PROJECT_ID}..."
gcloud builds submit --tag "${IMAGE_URI}" --project="${PROJECT_ID}" .

# 3. Deploy container image to Cloud Run
echo "🌐 [3/3] Deploying service to Cloud Run on ${PROJECT_ID}..."
gcloud run deploy "${SERVICE_NAME}" \
    --image="${IMAGE_URI}" \
    --platform=managed \
    --region="${REGION}" \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_REGION=${REGION},MODEL_NAME=gemini-3.5-flash" \
    --port=8080 \
    --project="${PROJECT_ID}"

# 4. Grant public unauthenticated access (allUsers -> roles/run.invoker)
echo "🔓 Granting public unauthenticated access (roles/run.invoker) to Cloud Run..."
gcloud run services add-iam-policy-binding "${SERVICE_NAME}" \
    --region="${REGION}" \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --project="${PROJECT_ID}" || true

echo "========================================================================="
echo "✅ Cloud Run Deployment Completed Successfully on ${PROJECT_ID}!"
echo "========================================================================="
