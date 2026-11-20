param([string]$Root = ".")
$ErrorActionPreference = "Stop"
$PluginDir = Split-Path -Parent $PSScriptRoot
& node (Join-Path $PluginDir "bin/deepsec-agent.mjs") scan --root $Root --format json --fail-on medium
exit $LASTEXITCODE
