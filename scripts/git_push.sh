#!/usr/bin/env bash
# StockSense AI - Auto Git Push
set -euo pipefail
COMMIT_MSG="${1:-"Auto-update $(date '+%Y-%m-%d %H:%M')"}"
BRANCH="${GIT_BRANCH:-main}"
git add -A
if git diff --cached --quiet; then
  echo "[git_push] Nothing to commit"
  exit 0
fi
git commit -m "$COMMIT_MSG"
VERSION_TAG="v$(date '+%Y%m%d-%H%M')"
git tag "$VERSION_TAG" || true
git push origin "$BRANCH" --follow-tags
echo "[git_push] Pushed '$COMMIT_MSG' ($VERSION_TAG)"
