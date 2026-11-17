#!/usr/bin/env bash
# The buzz-off machine: fetch block/buzz-app main, apply the prompt spec, build BuzzOff.app.
# usage: ./build.sh [--no-build]     (--no-build = just apply and show the diff)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; WORK="$HERE/.work"
PROMPT=src/features/agent-harness/base_prompt.md

[ -d "$WORK/.git" ] || git clone -q https://github.com/block/buzz-app.git "$WORK"
cd "$WORK"
git fetch -q origin main && git reset -q --hard origin/main && git clean -fdq
echo "upstream: $(git log -1 --format='%h %s')"

python3 "$HERE/strip_prompt.py" "$PROMPT"
cp "$HERE/tauri.buzzoff.conf.json" src-tauri/
git --no-pager diff --stat
git --no-pager diff -- "$PROMPT"

[ "${1:-}" = "--no-build" ] && exit 0
pnpm install --frozen-lockfile
pnpm tauri build --bundles app --config src-tauri/tauri.buzzoff.conf.json
APP=$(find "$WORK" -path '*/bundle/macos/BuzzOff.app' -maxdepth 7 -prune 2>/dev/null | head -1)
mkdir -p "$HERE/dist" && rm -rf "$HERE/dist/BuzzOff.app" && cp -R "$APP" "$HERE/dist/"
echo "built: $HERE/dist/BuzzOff.app"
