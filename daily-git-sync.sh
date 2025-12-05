#!/usr/bin/env bash
set -euo pipefail

echo "[git-sync] Repo: $(pwd)"

# Make sure we are on a branch (not detached HEAD)
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "[git-sync] Current branch: ${current_branch}"

echo "[git-sync] Fetching from origin..."
git fetch origin

echo "[git-sync] Pulling latest changes with rebase..."
git pull --rebase origin "${current_branch}" || {
  echo "[git-sync] git pull --rebase failed. Please resolve conflicts manually."
  exit 1
}

echo "[git-sync] Staging all changes..."
git add -A

if git diff --cached --quiet; then
  echo "[git-sync] No changes to commit."
else
  ts=$(date +"%Y-%m-%d %H:%M:%S")
  msg="auto-sync: ${ts}"
  echo "[git-sync] Committing with message: ${msg}"
  git commit -m "${msg}" || {
    echo "[git-sync] Commit failed. Check git status."
    exit 1
  }
fi

echo "[git-sync] Pushing to origin/${current_branch}..."
git push origin "${current_branch}"

echo "[git-sync] Done."
