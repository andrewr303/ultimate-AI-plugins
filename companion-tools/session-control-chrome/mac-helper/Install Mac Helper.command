#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
TASK_NODE="$(command -v node || true)"
if [ -z "$TASK_NODE" ]; then
  for candidate in /opt/homebrew/bin/node /usr/local/bin/node; do
    if [ -x "$candidate" ]; then TASK_NODE="$candidate"; break; fi
  done
fi
if [ -z "$TASK_NODE" ]; then
  echo "Install Node.js 22 or newer from https://nodejs.org, then run this installer again."
  read -r -p "Press Return to close. " unused
  exit 1
fi
echo "Session Control · Mac helper setup"
echo "Copy the extension ID from Session Control → Settings."
read -r -p "Extension ID: " TASK_EXTENSION_ID
"$TASK_NODE" install.cjs "$TASK_EXTENSION_ID"
read -r -p "Press Return to close. " unused
