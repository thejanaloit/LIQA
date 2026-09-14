# Customer Worker install check — fail closed if this PC cannot be watched.
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$env:LIQA_HOME = $Root
$env:LIQA_HEADED = "1"
if (-not $env:MANUAL_QA_HOME) {
  if (Test-Path (Join-Path $Root "mcp\device_core.py")) {
    $env:MANUAL_QA_HOME = $Root
  } elseif (Test-Path "E:\ManualQA-Agent\mcp\device_core.py") {
    $env:MANUAL_QA_HOME = "E:\ManualQA-Agent"
  }
}

Write-Host "LIQA verify-install"
Write-Host "  Python:" (py --version)
Write-Host "  LIQA_HOME=$env:LIQA_HOME"
Write-Host "  MANUAL_QA_HOME=$env:MANUAL_QA_HOME"

$hands = @(
  (Join-Path $Root "mcp\device_core.py"),
  (Join-Path ($env:MANUAL_QA_HOME) "mcp\device_core.py"),
  "E:\ManualQA-Agent\mcp\device_core.py"
) | Where-Object { $_ -and (Test-Path $_) }
if (-not $hands) {
  Write-Error "device_core missing. Expected under LIQA\mcp or MANUAL_QA_HOME\mcp."
}

$session = $env:SESSIONNAME
if ($session -in @("Services", "S-0")) {
  Write-Error "Session 0 / SERVICES — Worker needs an interactive desktop."
}
$logon = Get-Process LogonUI -ErrorAction SilentlyContinue
if ($logon) {
  Write-Error "LogonUI running — unlock the session."
}
$chrome = Get-Command chrome, msedge -ErrorAction SilentlyContinue
if (-not $chrome) {
  Write-Warning "Chrome/Edge not on PATH. Install a headed browser."
}
py -3 -c "import sys,os,json; sys.path.insert(0, r'$Root\apps\worker'); os.environ['LIQA_HOME']=r'$Root'; os.environ['MANUAL_QA_HOME']=os.environ.get('MANUAL_QA_HOME', r'$Root'); from health import headed_health; print(json.dumps(headed_health(), indent=2))"
Write-Host "verify-install done. Start Worker with .\scripts\bootstrap-worker-vm.ps1"
