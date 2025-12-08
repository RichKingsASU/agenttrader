#!/usr/bin/env bash
set -euo pipefail

# This script provides commands to build and deploy the Strategy Engine Cloud Run Job.

# --- Configuration ---
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
IMAGE_TAG="gcr.io/${PROJECT_ID}/agenttrader-strategy-engine"

# --- IAM Roles Required ---
# The user running these commands needs the following roles:
# - Cloud Build Editor (roles/cloudbuild.builds.editor)
# - Cloud Run Admin (roles/run.admin)
# - IAM Service Account User (roles/iam.serviceAccountUser)

# --- Build the container image ---
echo "Building and pushing the container image: ${IMAGE_TAG}"
# gcloud builds submit --config cloudbuild_strategy_engine.yaml .

# --- Deploy the Cloud Run Job ---
echo "Deploying the Cloud Run Job: agenttrader-strategy-engine"
# gcloud run jobs create agenttrader-strategy-engine \
#   --image "${IMAGE_TAG}" \
#   --region "${REGION}" \
#   --max-retries=3 \
#   --tasks=1 \
#   --set-env-vars="DATABASE_URL=${DATABASE_URL}" \
#   --set-env-vars="STRATEGY_NAME=naive_flow_trend" \
#   --set-env-vars="STRATEGY_SYMBOLS=SPY,IWM"

# --- Create a Cloud Scheduler Job ---
echo "Creating the Cloud Scheduler Job: agenttrader-strategy-engine-scheduler"
# This would trigger the job every minute during market hours.
# gcloud scheduler jobs create http agenttrader-strategy-engine-scheduler \
#   --schedule="* 9-16 * * 1-5" \
#   --time-zone="America/New_York" \
#   --uri="https://<YOUR_CLOUD_RUN_SERVICE_OR_API_ENDPOINT>" \
#   --http-method=POST \
#   --oauth-service-account-email="<YOUR_SERVICE_ACCOUNT_EMAIL>"
