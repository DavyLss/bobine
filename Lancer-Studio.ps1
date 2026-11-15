$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (!(Test-Path $python)) { throw 'Lancer Installer.ps1 avant le studio.' }
$localConfigPath = Join-Path $PSScriptRoot '.local/config.json'
$localConfig = if (Test-Path $localConfigPath) { Get-Content -Raw $localConfigPath | ConvertFrom-Json } else { $null }
$studioPort = if ($env:STUDIO_PORT) { [int]$env:STUDIO_PORT } elseif ($localConfig -and $localConfig.STUDIO_PORT) { [int]$localConfig.STUDIO_PORT } else { 8510 }
$url = "http://127.0.0.1:$studioPort"
$running = $false
try { $null = Invoke-RestMethod "$url/api/state" -TimeoutSec 2; $running = $true } catch { }
if (!$running) {
    $logs = Join-Path $PSScriptRoot '.local'
    New-Item -ItemType Directory -Force -Path $logs | Out-Null
    $entry = Join-Path $PSScriptRoot 'studio/server.py'
    Start-Process -FilePath $python -ArgumentList @('-u', ('"' + $entry + '"')) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput "$logs/server.log" -RedirectStandardError "$logs/server-error.log" | Out-Null
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        Start-Sleep -Milliseconds 500
        try { $null = Invoke-RestMethod "$url/api/state" -TimeoutSec 1; $running = $true; break } catch { }
    }
    if (!$running) { throw "Serveur indisponible : consulter $logs/server-error.log" }
}
Start-Process $url
