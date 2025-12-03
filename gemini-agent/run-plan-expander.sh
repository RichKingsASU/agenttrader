#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./gemini-agent/run-plan-expander.sh INPUT_PLAN_FILE [OUTPUT_FILE]
#
# Example:
#   ./gemini-agent/run-plan-expander.sh docs/plans/foo.txt docs/blueprints/foo_blueprint.md

MODEL="models/gemini-2.0-flash"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 INPUT_PLAN_FILE [OUTPUT_FILE]"
  exit 1
fi

PLAN_FILE="$1"
OUTPUT_FILE="${2:-docs/blueprints/blueprint_$(date +%Y%m%d_%H%M%S).md}"
SYSTEM_FILE="$SCRIPT_DIR/system_instruction.txt"

if [[ -z "${GEMINI_API_KEY:-}" ]]; then
  echo "ERROR: GEMINI_API_KEY is not set. Export it first."
  exit 1
fi

if [[ ! -f "$PLAN_FILE" ]]; then
  echo "ERROR: Plan file not found: $PLAN_FILE"
  exit 1
fi

if [[ ! -f "$SYSTEM_FILE" ]]; then
  echo "ERROR: System instruction file not found: $SYSTEM_FILE"
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

echo "Using model: $MODEL"
echo "Input plan: $PLAN_FILE"
echo "Output file: $OUTPUT_FILE"

SYSTEM_TEXT=$(jq -Rs . < "$SYSTEM_FILE")
PLAN_TEXT=$(jq -Rs . < "$PLAN_FILE")

RESPONSE=$(curl -sS -X POST \
  "https://generativelanguage.googleapis.com/v1beta/${MODEL}:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [
      { \"role\": \"user\", \"parts\": [ { \"text\": ${SYSTEM_TEXT} } ] },
      { \"role\": \"user\", \"parts\": [ { \"text\": ${PLAN_TEXT} } ] }
    ]
  }")

echo "$RESPONSE" | jq -r '.candidates[0].content.parts[0].text' > "$OUTPUT_FILE"

echo "✅ Blueprint written to: $OUTPUT_FILE"
