# Support bundle — no .env, no vault, no passwords.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Tmp = Join-Path $env:TEMP "liqa-support"
if (Test-Path $Tmp) { Remove-Item $Tmp -Recurse -Force }
New-Item $Tmp -ItemType Directory | Out-Null
Copy-Item "$Root\docs" $Tmp -Recurse
if (Test-Path "$Root\apps\control\data\audit") { Copy-Item "$Root\apps\control\data\audit" "$Tmp\audit" -Recurse }
py -c "import json,urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8787/health',timeout=5).read().decode())" | Out-File "$Tmp\health-worker.json"
$Out = Join-Path $Root "reports\support-bundle.zip"
Compress-Archive -Path $Tmp -DestinationPath $Out -Force
Write-Host $Out
