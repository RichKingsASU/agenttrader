#!/bin/bash

# This script provides commands to build and deploy the
# AgentTrader Strategy Engine to Google Cloud Run as a Job.

# --- Configuration ---
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="agenttrader-strategy-engine"
REGION="us-central1"
IMAGE_URI="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
SERVICE_ACCOUNT="my-run-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# --- Add IAM policy binding ---
echo "Adding IAM policy binding..."
gcloud run jobs add-iam-policy-binding "${SERVICE_NAME}" \
  --region="${REGION}" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/run.invoker"

# --- Build and Push Container Image ---
echo "Building and pushing container image..."
gcloud builds submit --config cloudbuild_strategy_engine.yaml .

# --- Deploy to Cloud Run as a Job ---
echo "Deploying to Cloud Run as a Job..."
# Note: This command assumes you have a secret named 'DATABASE_URL' in Secret Manager.
gcloud run jobs deploy "${SERVICE_NAME}" \
  --image "${IMAGE_URI}" \
  --region "${REGION}" \
  --service-account "${SERVICE_ACCOUNT}" \
  --set-secrets="DATABASE_URL=DATABASE_URL:latest" \
  --update-env-vars="STRATEGY_NAME=naive_flow_trend,STRATEGY_SYMBOLS=SPY IWM QQQ,STRATEGY_BAR_LOOKBACK_MINUTES=30,STRATEGY_FLOW_LOOKBACK_MINUTES=5"

# --- Delete Existing Cloud Scheduler Job ---
echo "Deleting existing Cloud Scheduler Job..."
gcloud scheduler jobs delete "${SERVICE_NAME}-scheduler" --location="${REGION}" --quiet

# --- Create Cloud Scheduler Job ---
echo "Creating Cloud Scheduler Job..."
gcloud scheduler jobs create http "${SERVICE_NAME}-scheduler" \
  --schedule "*/5 13-20 * * 1-5" \
  --location "${REGION}" \
  --uri "https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${SERVICE_NAME}:run" \
  --http-method "POST" \
  --oidc-service-account-email "${SERVICE_ACCOUNT}"
