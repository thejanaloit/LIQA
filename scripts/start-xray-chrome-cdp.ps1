# Start a dedicated Chrome with remote debugging for LIQA Xray UI RPA.
# 1) Run this script
# 2) Log into Jira once in that window (OTP yourself)
# 3) Upload:
#      $env:LIQA_CHROME_CDP = "http://127.0.0.1:9333"
#      py -3 E:\LIQA\scripts\xray_ui_upload_end_of_run.py upload

$ErrorActionPreference = "Stop"
$port = 9333
$profile = "E:\LIQA\workspace\default-run\.chrome-xray-cdp"
New-Item -ItemType Directory -Force -Path $profile | Out-Null

$chromeCandidates = @(
  "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
$chrome = $chromeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) { throw "Chrome not found" }

# Avoid clashing with normal Chrome: separate user-data-dir + debug port
Start-Process -FilePath $chrome -ArgumentList @(
  "--remote-debugging-port=$port",
  "--user-data-dir=$profile",
  "--no-first-run",
  "--no-default-browser-check",
  "https://lolcgroupdev.atlassian.net/browse/PF-59477"
)

Write-Host "Chrome CDP listening on http://127.0.0.1:$port"
Write-Host "Log into Jira in that window, then:"
Write-Host '  $env:LIQA_CHROME_CDP = "http://127.0.0.1:9333"'
Write-Host "  py -3 E:\LIQA\scripts\xray_ui_upload_end_of_run.py upload"
