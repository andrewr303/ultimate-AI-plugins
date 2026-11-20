#!/bin/bash
set -euo pipefail
TASK_BRIDGE="$HOME/Library/Application Support/SessionControlChrome/Bridge"
TASK_MANIFEST="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.sessioncontrol.chrome.json"
echo "This removes the Session Control launcher. Account Chrome profiles and their logins will be kept."
read -r -p "Type REMOVE to continue: " TASK_ANSWER
if [ "$TASK_ANSWER" != REMOVE ]; then exit 0; fi
rm -f -- "$TASK_MANIFEST" "$TASK_BRIDGE/launch-host" "$TASK_BRIDGE/config.json" "$TASK_BRIDGE/host.cjs" "$TASK_BRIDGE/core.cjs"
echo "Helper removed. Your dedicated account profiles remain in:"
echo "$HOME/Library/Application Support/SessionControlChrome/Profiles"
read -r -p "Press Return to close. " unused
