# Bootstrap LIQA Worker VM (interactive desktop required)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Write-Host "LIQA Worker VM bootstrap → $Root"

$session = $env:SESSIONNAME
if ($session -in @("Services", "S-0")) {
  throw "Session 0 / SERVICES — log into an interactive desktop first (autologon user)."
}

$envFile = Join-Path $Root ".env"
if (-not (Test-Path $envFile)) {
  Copy-Item (Join-Path $Root ".env.example") $envFile
  Write-Host "Created .env — set LIQA_CONTROL_URL and vault paths."
}

$secretsExample = Join-Path $Root "secrets\tmp-creds.example.json"
$secrets = Join-Path $Root "secrets\tmp-creds.json"
if (-not (Test-Path $secrets)) {
  New-Item -ItemType Directory -Force -Path (Join-Path $Root "secrets") | Out-Null
  if (Test-Path $secretsExample) { Copy-Item $secretsExample $secrets }
  Write-Host "WARN: fill secrets\tmp-creds.json from vault (never commit)."
}

$env:LIQA_HOME = $Root
$env:LIQA_HEADED = "1"
if (-not $env:MANUAL_QA_HOME) {
  if (Test-Path (Join-Path $Root "mcp\device_core.py")) { $env:MANUAL_QA_HOME = $Root }
}
$env:LIQA_WORKER_HOST = if ($env:LIQA_WORKER_HOST) { $env:LIQA_WORKER_HOST } else { "127.0.0.1" }
$env:LIQA_WORKER_PORT = if ($env:LIQA_WORKER_PORT) { $env:LIQA_WORKER_PORT } else { "8787" }
$env:LIQA_CONTROL_URL = if ($env:LIQA_CONTROL_URL) { $env:LIQA_CONTROL_URL } else { "http://127.0.0.1:8788" }
$env:LIQA_WORKER_ID = if ($env:LIQA_WORKER_ID) { $env:LIQA_WORKER_ID } else { $env:COMPUTERNAME }

# Power: never sleep (best-effort)
try {
  powercfg /change standby-timeout-ac 0 | Out-Null
  powercfg /change monitor-timeout-ac 0 | Out-Null
} catch {}

Write-Host "Worker id: $env:LIQA_WORKER_ID"
Write-Host "Control:   $env:LIQA_CONTROL_URL"
Write-Host "Next: verify-install.ps1 then register-logon-task.ps1"
Write-Host "Starting Worker API…"

py -3 (Join-Path $Root "apps\worker\api.py")
