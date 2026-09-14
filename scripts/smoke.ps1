$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$env:MANUAL_QA_HOME = if ($env:MANUAL_QA_HOME) { $env:MANUAL_QA_HOME } else { "E:\QAFusionX\manualQA" }
$env:LIQA_HEADED = "1"
Set-Location $Root
py -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "SMOKE unit tests PASS"
try {
  $c = Invoke-RestMethod http://127.0.0.1:8788/health
  $w = Invoke-WebRequest http://127.0.0.1:8787/health -UseBasicParsing
  Write-Host "live control ok=$($c.ok) worker status=$($w.StatusCode)"
} catch { Write-Host "live /health skipped (servers not up): $_" }
