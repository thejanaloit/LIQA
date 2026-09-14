# Build the FINAL LIQA handover zip (includes QA-trained agency pack)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$OutDir = Join-Path $Root "packaging\out"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmm"
$Zip = Join-Path $OutDir "LIQA-FINAL-PACKAGE-$stamp.zip"

# Ensure training exists
py -3 (Join-Path $Root "scripts\train_agency_qa.py") | Out-Host

$stage = Join-Path $env:TEMP "liqa-final-$stamp"
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

@"
LIQA FINAL PACKAGE
Built: $stamp
Agency QA-trained: packaging/industry/agency-qa-trained/ (279 overlays)
Read: docs/FINAL-PACKAGE.md
Install: py -3 scripts/install_liqa_mcp.py
Gate: py -3 -m pytest tests/test_same_level_contract.py tests/test_industry_ops_model.py -q
"@ | Set-Content (Join-Path $stage "FINAL-README.txt") -Encoding utf8

Copy-Item (Join-Path $Root "docs\FINAL-PACKAGE.md") (Join-Path $stage "docs\FINAL-PACKAGE.md") -Force

if (Test-Path $Zip) { Remove-Item $Zip -Force }
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $Zip -Force
Remove-Item -Recurse -Force $stage

# Also write a pointer file next to zip
@"
# LIQA FINAL PACKAGE

Zip: $Zip
Open docs/FINAL-PACKAGE.md after unzip.
QA-trained agency specialists: 279
"@ | Set-Content (Join-Path $OutDir "LIQA-FINAL-PACKAGE-LATEST.txt") -Encoding utf8

Write-Host "FINAL PACKAGE: $Zip"
Get-Item $Zip | Format-List FullName, Length, LastWriteTime
