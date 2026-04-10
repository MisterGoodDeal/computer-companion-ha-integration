#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 patch|minor|major" >&2
  echo "  Bumps version in manifest.json, commits, creates annotated tag vX.Y.Z, pushes branch + tag." >&2
  exit 1
}

MODE="${1:-}"
case "$MODE" in
  patch | minor | major) ;;
  *) usage ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
  echo "error: not inside a git repository" >&2
  exit 1
}
cd "$REPO_ROOT"

MANIFEST="custom_components/computer_companion/manifest.json"
[[ -f "$MANIFEST" ]] || {
  echo "error: missing $MANIFEST" >&2
  exit 1
}

if ! git diff-index --quiet HEAD -- 2>/dev/null; then
  echo "error: working tree is not clean. Commit or stash changes first." >&2
  exit 1
fi

export RELEASE_MODE="$MODE"
NEW_VERSION="$(
  python3 << 'PY'
import json
import os
import sys

mode = os.environ["RELEASE_MODE"]
path = "custom_components/computer_companion/manifest.json"
with open(path, encoding="utf-8") as f:
    data = json.load(f)
current = data["version"]
parts = [int(x) for x in current.split(".")]
while len(parts) < 3:
    parts.append(0)
major, minor, patch = parts[0], parts[1], parts[2]
if mode == "patch":
    patch += 1
elif mode == "minor":
    minor += 1
    patch = 0
elif mode == "major":
    major += 1
    minor = 0
    patch = 0
data["version"] = f"{major}.{minor}.{patch}"
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(data["version"])
PY
)"

echo "New version: $NEW_VERSION"

git add "$MANIFEST"
git commit -m "chore: release v${NEW_VERSION}"

TAG="v${NEW_VERSION}"
git tag -a "$TAG" -m "Release ${TAG}"

CURRENT_BRANCH="$(git branch --show-current)"
REMOTE="${REMOTE:-origin}"

echo "Pushing branch '${CURRENT_BRANCH}' and tag '${TAG}' to ${REMOTE}..."
git push "$REMOTE" "$CURRENT_BRANCH"
git push "$REMOTE" "$TAG"

echo "Done: ${TAG} published on ${REMOTE}."
