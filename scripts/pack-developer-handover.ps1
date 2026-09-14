# Pack LIQA for other developers (excludes secrets / captures / caches)
$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
# script is E:\LIQA\scripts\... → root is E:\LIQA
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$OutDir = Join-Path $Root "packaging\out"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmm"
$Zip = Join-Path $OutDir "LIQA-developer-handover-$stamp.zip"

$stage = Join-Path $env:TEMP "liqa-handover-$stamp"
if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Force -Path $stage | Out-Null

$excludeDirs = @(
  '.git', '__pycache__', 'captures', 'node_modules', 'vendor\oss',
  'apps\control\data', '.venv', 'packaging\out'
)
$excludeFiles = @('.env', 'tmp-creds.json', 'session.json')

function ShouldSkip([string]$full) {
  $rel = $full.Substring($Root.Length).TrimStart('\','/')
  foreach ($d in $excludeDirs) {
    if ($rel -like "$d*") { return $true }
  }
  $name = Split-Path $full -Leaf
  if ($excludeFiles -contains $name) { return $true }
  if ($name -like '*.pyc') { return $true }
  return $false
}

Get-ChildItem $Root -Recurse -File | ForEach-Object {
  if (ShouldSkip $_.FullName) { return }
  $rel = $_.FullName.Substring($Root.Length).TrimStart('\','/')
  $dest = Join-Path $stage $rel
  $destParent = Split-Path $dest -Parent
  if (-not (Test-Path $destParent)) { New-Item -ItemType Directory -Force -Path $destParent | Out-Null }
  Copy-Item $_.FullName $dest -Force
}

# Ensure handover docs + example secrets are present
Copy-Item (Join-Path $Root "docs\QUALITY-CONTRACT.md") (Join-Path $stage "docs\QUALITY-CONTRACT.md") -Force -ErrorAction SilentlyContinue
Copy-Item (Join-Path $Root "secrets\tmp-creds.example.json") (Join-Path $stage "secrets\tmp-creds.example.json") -Force -ErrorAction SilentlyContinue

# Manifest
@"
LIQA Developer Handover
Built: $stamp
Read first: docs/DEVELOPER-HANDOVER.md
Quality bar: docs/QUALITY-CONTRACT.md
Acceptance: docs/SAME-LEVEL-ACCEPTANCE.md
Install: py -3 scripts/install_liqa_mcp.py
Gate: py -3 -m pytest tests/test_same_level_contract.py -q
"@ | Set-Content (Join-Path $stage "HANDOVER-README.txt") -Encoding utf8

if (Test-Path $Zip) { Remove-Item $Zip -Force }
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $Zip -Force
Remove-Item -Recurse -Force $stage
Write-Host "Handover zip: $Zip"
Get-Item $Zip | Format-List FullName, Length, LastWriteTime
