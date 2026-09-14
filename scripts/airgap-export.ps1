# Air-gap zip of reports + captures without Control SaaS.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Out = Join-Path $Root "reports\airgap-$(Get-Date -Format yyyyMMdd-HHmm).zip"
if (-not (Test-Path "$Root\reports")) { New-Item -ItemType Directory -Path "$Root\reports" | Out-Null }
Compress-Archive -Path @("$Root\reports","$Root\docs") -DestinationPath $Out -Force
Write-Host $Out
