param([switch]$Navigateur)
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
if ($Navigateur) {
    Start-Process $url
    return
}
# Chromium app mode reuses an installed browser, with a profile reserved for Bobine.
$appBrowser = $null
foreach ($browserName in @('msedge.exe', 'chrome.exe', 'brave.exe')) {
    foreach ($hive in @('HKCU:', 'HKLM:')) {
        $appPath = Get-ItemProperty "$hive/Software/Microsoft/Windows/CurrentVersion/App Paths/$browserName" -ErrorAction SilentlyContinue
        $candidate = if ($appPath) { $appPath.'(default)' } else { $null }
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) { $appBrowser = $candidate; break }
    }
    if ($appBrowser) { break }
}
if (!$appBrowser) {
    foreach ($relative in @('Microsoft/Edge/Application/msedge.exe', 'Google/Chrome/Application/chrome.exe', 'BraveSoftware/Brave-Browser/Application/brave.exe')) {
        foreach ($base in @($env:ProgramFiles, ${env:ProgramFiles(x86)}, $env:LOCALAPPDATA)) {
            if (!$base) { continue }
            $candidate = Join-Path $base $relative
            if (Test-Path -LiteralPath $candidate -PathType Leaf) { $appBrowser = $candidate; break }
        }
        if ($appBrowser) { break }
    }
}
if (!$appBrowser) { throw 'Installer Edge, Chrome ou Brave pour la fenêtre dédiée, ou lancer .\Lancer-Studio.ps1 -Navigateur.' }
$appProfile = Join-Path $PSScriptRoot '.local/app-profile'
Start-Process -FilePath $appBrowser -ArgumentList @("--app=$url", ('--user-data-dir="' + $appProfile + '"'), '--no-first-run', '--no-default-browser-check')
