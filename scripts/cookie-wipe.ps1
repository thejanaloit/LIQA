# Close Chrome only when no LIQA session.lock / session.json open.
$sess = "E:\LIQA\apps\worker\session.json"
if (Test-Path $sess) {
  $j = Get-Content $sess -Raw | ConvertFrom-Json
  if ($j.open) { Write-Error "Job in session — will not wipe cookies mid-job"; exit 1 }
}
$ud = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default"
Write-Host "Manual: close Chrome then delete Cookies under $ud only on a shared appliance between customers."
