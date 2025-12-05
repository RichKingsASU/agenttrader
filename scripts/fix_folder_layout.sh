#!/usr/bin/env bash
set -euo pipefail

# Always run from repo root
cd "$(dirname "$0")/.."

echo "[layout] Saving current tree to tree_before_layout_fix.txt..."
ls -R > tree_before_layout_fix.txt

echo "[layout] Current git status (short):"
git status -sb || true
echo

# 1) Kill the obvious junk file from that accidental command
if [ -f 'ql "$DATABASE_URL" -c "' ]; then
  echo '[layout] Removing stray file: ql "$DATABASE_URL" -c "'
  rm -f 'ql "$DATABASE_URL" -c "'
fi

# 2) Archive any untracked top-level dirs that look like dupes/old projects
ARCHIVE_DIR="z_orphan_dirs_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

# Add any other suspicious top-level dirs to this list if needed
CANDIDATES=("backend" "docs" "prompts" "supabase" "dexter")

for d in "${CANDIDATES[@]}"; do
  if [ -d "$d" ]; then
    if git ls-files --error-unmatch "$d" >/dev/null 2>&1; then
      echo "[layout] Keeping git-tracked dir: $d"
    else
      echo "[layout] Archiving untracked dir: $d -> $ARCHIVE_DIR/$d"
      mv "$d" "$ARCHIVE_DIR/$d"
    fi
  fi
done

echo
echo "[layout] New git status (short):"
git status -sb || true

echo
echo "[layout] Done."
echo " - Original tree saved to: tree_before_layout_fix.txt"
echo " - Any untracked/extra dirs moved into: $ARCHIVE_DIR/"
