#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR%/gemini-agent}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 path/to_high_level_plan.txt [output_file.md]"
  exit 1
fi

PLAN_FILE="$1"
OUTPUT_FILE="${2:-"$REPO_ROOT/docs/blueprints/blueprint_$(date +%Y%m%d_%H%M%S).md"}"

MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"

if [[ ! -f "$PLAN_FILE" ]]; then
  echo "Plan file not found: $PLAN_FILE"
  exit 1
fi

SYSTEM_TEXT="$(cat "$SCRIPT_DIR/system_instruction.txt")"
PLAN_TEXT="$(cat "$PLAN_FILE")"

PROMPT=$(cat <<EOF
$SYSTEM_TEXT

High-level plan:

$PLAN_TEXT
EOF
)

echo "Using model: $MODEL"
echo "Input plan: $PLAN_FILE"
echo "Output file: $OUTPUT_FILE"

mkdir -p "$(dirname "$OUTPUT_FILE")"

gemini -m "$MODEL" -p "$PROMPT" > "$OUTPUT_FILE"

echo "Done. Expanded blueprint written to: $OUTPUT_FILE"