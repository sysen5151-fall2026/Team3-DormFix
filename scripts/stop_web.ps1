$Root = Split-Path -Parent $PSScriptRoot
$PidFile = Join-Path $Root 'data\dormfix-web.pid'
if (Test-Path $PidFile) { $id = Get-Content $PidFile | Select-Object -First 1; if ($id) { Stop-Process -Id ([int]$id) -Force -ErrorAction SilentlyContinue }; Remove-Item $PidFile -Force -ErrorAction SilentlyContinue; Write-Host 'DormFix stopped.' } else { Write-Host 'No DormFix PID file found.' }
