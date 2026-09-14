# Bootstrap LIQA Control host (industry)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Write-Host "LIQA Control bootstrap → $Root"

$envFile = Join-Path $Root ".env"
if (-not (Test-Path $envFile)) {
  Copy-Item (Join-Path $Root ".env.example") $envFile
  Write-Host "Created .env from example — set LIQA_CONTROL_TOKEN before production."
}

$env:LIQA_CONTROL_HOST = if ($env:LIQA_CONTROL_HOST) { $env:LIQA_CONTROL_HOST } else { "0.0.0.0" }
$env:LIQA_CONTROL_PORT = if ($env:LIQA_CONTROL_PORT) { $env:LIQA_CONTROL_PORT } else { "8788" }

New-Item -ItemType Directory -Force -Path (Join-Path $Root "apps\control\data") | Out-Null

Write-Host "Starting Control on http://$($env:LIQA_CONTROL_HOST):$($env:LIQA_CONTROL_PORT)/"
Write-Host "2QA console: open / in browser — gates + sign-off"
Write-Host "Docs: docs\INDUSTRY-PRODUCT.md , docs\OPS-MODEL-2QA.md"

py -3 (Join-Path $Root "apps\control\server.py")
