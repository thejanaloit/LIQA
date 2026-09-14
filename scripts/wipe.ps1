# Wipe captures, jobs, gates, trajectories. Never deletes .env unless -AllSecrets (don't).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
foreach ($d in @("captures","trajectories","reports","apps\worker\jobs","apps\worker\gates","apps\control\data\jobs","apps\control\data\gates","apps\control\data\artifacts")) {
  $p = Join-Path $Root $d
  if (Test-Path $p) { Get-ChildItem $p -Recurse -File | Where-Object { $_.Name -ne "README.txt" } | Remove-Item -Force }
}
Write-Host "LIQA wipe done (secrets/.env kept)"
