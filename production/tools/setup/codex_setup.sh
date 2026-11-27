#!/usr/bin/env bash
# One-tap Codex setup for a new cloud session. Safe to run again at any time.
# Installs the Codex CLI if missing, makes the login file-based, and, if not logged in,
# starts the device login and prints the link and one-time code for the owner to approve.
# Nothing secret is written to the repo. See production/IMAGE-PIPELINE.md.
set -u
LOG="${1:-/tmp/codex-login.log}"
if ! command -v codex >/dev/null 2>&1; then
  npm install -g @openai/codex >/dev/null 2>&1 || { echo "CODEX: install failed"; exit 1; }
fi
mkdir -p "$HOME/.codex"
grep -q cli_auth_credentials_store "$HOME/.codex/config.toml" 2>/dev/null || \
  echo 'cli_auth_credentials_store = "file"' >> "$HOME/.codex/config.toml"
if codex login status 2>&1 | grep -qi "logged in"; then
  echo "CODEX: already logged in ($(codex --version 2>/dev/null))"; exit 0
fi
: > "$LOG"
nohup codex login --device-auth > "$LOG" 2>&1 &
for _ in $(seq 1 40); do
  grep -q -i "one-time code" "$LOG" 2>/dev/null && break
  read -r -t 0.5 _ < /dev/zero 2>/dev/null || true
done
echo "CODEX: login needed. Give the owner this link and code (valid 15 minutes):"
sed 's/\x1b\[[0-9;]*m//g' "$LOG" | grep -E -A1 "https://|one-time code" | grep -v "^--$"
echo "CODEX: after approval, check with: codex login status"
