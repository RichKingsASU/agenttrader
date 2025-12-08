#!/bin/bash

# This script provides commented-out commands to build and deploy the
# AgentTrader Strategy Engine to Google Cloud Run.

# --- Configuration ---
# GCP Project ID
# PROJECT_ID="your-gcp-project-id"

# Cloud Run service name
# SERVICE_NAME="agenttrader-strategy-engine"

# GCP region
# REGION="us-central1"

# Container image URI
# IMAGE_URI="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# --- Build and Push Container Image ---
# gcloud builds submit --config cloudbuild_strategy_engine.yaml .

# --- Deploy to Cloud Run ---
# Make sure to replace the environment variable values with your actual secrets.
# gcloud run deploy "${SERVICE_NAME}" \
#   --image "${IMAGE_URI}" \
#   --region "${REGION}" \
#   --platform "managed" \
#   --no-allow-unauthenticated \
#   --set-env-vars="DATABASE_URL=your-supabase-database-url" \
#   --set-env-vars="STRATEGY_NAME=naive_flow_trend" \
#   --set-env-vars="STRATEGY_SYMBOLS=SPY,IWM,QQQ" \
#   --set-env-vars="STRATEGY_BAR_LOOKBACK_MINUTES=30" \
#   --set-env-vars="STRATEGY_FLOW_LOOKBACK_MINUTES=5"

# --- Create Cloud Scheduler Job ---
# This example creates a job that runs every 15 minutes.
# gcloud scheduler jobs create http "${SERVICE_NAME}-scheduler" \
#   --schedule "*/15 * * * *" \
#   --uri "https://$(gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format 'value(status.url)' | cut -d'/' -f3)" \
#   --http-method "POST" \
#   --oidc-service-account-email "$(gcloud projects describe "${PROJECT_ID}" --format 'value(projectNumber)')-compute@developer.gserviceaccount.com"