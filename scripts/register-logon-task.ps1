# Register LIQA Worker to start at user logon (interactive session).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$py = (Get-Command py).Source
$worker = Join-Path $Root "apps\worker\api.py"
$action = New-ScheduledTaskAction -Execute $py -Argument "`"$worker`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName "LIQA-Worker" -Action $action -Trigger $trigger -Principal $principal -Force
Write-Host "Registered LIQA-Worker at logon. Confirm an interactive desktop — Session 0 will fail /health."
