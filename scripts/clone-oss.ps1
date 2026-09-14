# Shallow-clone reference OSS (permissive licenses). Gitignored under vendor/oss.
$ErrorActionPreference = "Continue"
$Dest = Join-Path (Split-Path -Parent $PSScriptRoot) "vendor\oss"
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$repos = @(
  @{ name = "steel-browser"; url = "https://github.com/steel-dev/steel-browser.git" },
  @{ name = "midscene"; url = "https://github.com/web-infra-dev/midscene.git" },
  @{ name = "computer-use-mcp"; url = "https://github.com/zavora-ai/computer-use-mcp.git" }
)
foreach ($r in $repos) {
  $p = Join-Path $Dest $r.name
  if (Test-Path $p) { Write-Host "exists $($r.name)"; continue }
  Write-Host "clone $($r.name)"
  git clone --depth 1 $r.url $p
}
Write-Host "done. See vendor/REFERENCES.md"
