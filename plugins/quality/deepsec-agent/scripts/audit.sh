#!/usr/bin/env sh
set -eu
plugin_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
node "$plugin_dir/bin/deepsec-agent.mjs" scan --root "${1:-.}" --format json --fail-on medium
