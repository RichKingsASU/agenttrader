#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./run-plan-expander.sh path/to/high_level_plan.txt [output_file.md]
#
# Requires:
#   - Gemini CLI installed and authenticated
#   - GEMINI_MODEL (optional)
#   - agent_config.json and system_instruction.txt in same directory

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 path/to/high_level_plan.txt [output_file.md]"
  exit 1
fi

PLAN_FILE="$1"
OUTPUT_FILE="${2:-full_system_blueprint.md}"

MODEL="${GEMINI_MODEL:-gemini-2.0-flash-thinking}"

echo "Using model: $MODEL"
echo "Input plan: $PLAN_FILE"
echo "Output file: $OUTPUT_FILE"

gemini run \
  -m "$MODEL" \
  --config "$SCRIPT_DIR/agent_config.json" \
  --input-file "$PLAN_FILE" \
  > "$OUTPUT_FILE"

echo "Done. Expanded blueprint written to: $OUTPUT_FILE"
