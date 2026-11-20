#!/bin/sh
# Read-only environment evidence. Does not install tools or alter Xcode selection.
set -u
if [ "$(uname -s)" != "Darwin" ]; then
  echo 'macOS validation unavailable: run this script on the target Mac.'
  exit 2
fi
sw_vers
uname -m
if command -v xcode-select >/dev/null 2>&1; then
  xcode-select -p
else
  echo 'xcode-select unavailable'
fi
if command -v xcodebuild >/dev/null 2>&1; then
  xcodebuild -version
else
  echo 'xcodebuild unavailable; full Xcode may be required'
fi
if command -v xcrun >/dev/null 2>&1; then
  xcrun --sdk macosx --show-sdk-version
fi
