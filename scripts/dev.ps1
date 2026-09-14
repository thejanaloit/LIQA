# Optional: open Control UI after start.
param([switch]$OpenUi)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$env:MANUAL_QA_HOME = if ($env:MANUAL_QA_HOME) { $env:MANUAL_QA_HOME } else { "E:\QAFusionX\manualQA" }
$env:LIQA_HEADED = "1"
$env:PYTHONUNBUFFERED = "1"
function Listening($port) {
  return [bool](netstat -ano | Select-String ":$port " | Select-String "LISTENING")
}
if (-not (Listening 8788)) {
  Start-Process py -ArgumentList "-u `"$Root\apps\control\server.py`"" -WindowStyle Minimized
}
if (-not (Listening 8787)) {
  Start-Process py -ArgumentList "-u `"$Root\apps\worker\api.py`"" -WindowStyle Minimized
}
Write-Host "LIQA Control http://127.0.0.1:8788/  Worker http://127.0.0.1:8787/health"
if ($OpenUi) { Start-Process "http://127.0.0.1:8788/" }
