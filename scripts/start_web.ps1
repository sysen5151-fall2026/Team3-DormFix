$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Data = Join-Path $Root 'data'
New-Item -ItemType Directory -Path $Data -Force | Out-Null
$PidFile = Join-Path $Data 'dormfix-web.pid'
$Log = Join-Path $Data 'dormfix-web.log'
$Port = if ($env:DORMFIX_PORT) { [int]$env:DORMFIX_PORT } else { 8502 }

function Test-Site { try { $r=Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 -Uri "http://127.0.0.1:$Port"; return $r.StatusCode -eq 200 } catch { return $false } }
if (Test-Site) { Start-Process "http://127.0.0.1:$Port"; exit 0 }

$Py = Get-Command py -ErrorAction SilentlyContinue
if ($Py) { $File=$Py.Source; $Args=@('-3','webapp.py','--port',"$Port") }
else { $Py = Get-Command python -ErrorAction SilentlyContinue; if (-not $Py) { throw 'Python 3 not found.' }; $File=$Py.Source; $Args=@('webapp.py','--port',"$Port") }

$p = Start-Process -FilePath $File -ArgumentList $Args -WorkingDirectory $Root -WindowStyle Hidden -PassThru -RedirectStandardOutput $Log -RedirectStandardError (Join-Path $Data 'dormfix-web-error.log')
$p.Id | Set-Content -Path $PidFile -Encoding ascii
for ($i=0; $i -lt 30; $i++) { Start-Sleep -Milliseconds 500; if (Test-Site) { Start-Process "http://127.0.0.1:$Port"; Write-Host "DormFix ready: http://127.0.0.1:$Port"; exit 0 }; if ($p.HasExited) { break } }
Write-Host 'DormFix did not start. Check data\dormfix-web-error.log.'
exit 1
