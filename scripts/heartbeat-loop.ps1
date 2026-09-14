# Outbound heartbeat every 15s.
$env:MANUAL_QA_HOME = if ($env:MANUAL_QA_HOME) { $env:MANUAL_QA_HOME } else { "E:\QAFusionX\manualQA" }
$env:LIQA_HEADED = "1"
while ($true) {
  try { Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8787/v1/heartbeat -ContentType application/json -Body "{}" | Out-Null }
  catch { Write-Host "heartbeat fail $_" }
  Start-Sleep -Seconds 15
}
