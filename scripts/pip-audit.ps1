$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
py -m pip_audit -r apps/worker/requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Host "pip-audit missing or findings — install pip-audit or review freeze" }
py -m pip freeze | Out-File reports\sbom-pip-freeze.txt -Encoding utf8
Write-Host "SBOM freeze written"
