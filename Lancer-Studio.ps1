param([switch]$Navigateur, [switch]$SansZone)
$ErrorActionPreference = 'Stop'
if (!$Navigateur -and !$SansZone) {
    $trayHost = Join-Path $env:SystemRoot 'System32/WindowsPowerShell/v1.0/powershell.exe'
    $trayEntry = Join-Path $PSScriptRoot 'Bobine-Tray.ps1'
    $trayArguments = @('-NoProfile', '-STA', '-WindowStyle', 'Hidden', '-File', ('"' + $trayEntry + '"'))
    Start-Process -FilePath $trayHost -ArgumentList $trayArguments -WindowStyle Hidden
    return
}
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
$desktopEntry = Join-Path $PSScriptRoot 'studio/desktop.py'
$desktopPython = Join-Path $PSScriptRoot '.venv/Scripts/pythonw.exe'
if (!(Test-Path -LiteralPath $desktopPython)) { throw 'Exécuter Installer-Fenetre.ps1 pour installer la fenêtre Bobine.' }
$desktopKey = [IO.Path]::GetFullPath($desktopEntry).Replace('\','/').ToLowerInvariant()
$hostStarted = $false
foreach ($hostProcess in @(Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'")) {
    $command = ([string]$hostProcess.CommandLine).Replace('\','/').ToLowerInvariant()
    if ($command.Contains($desktopKey)) {
        $hostStarted = $true
        $existing = Get-Process -Id $hostProcess.ProcessId -ErrorAction SilentlyContinue
        if ($existing -and $existing.MainWindowHandle -ne [IntPtr]::Zero) {
            if (!('BobineWindow' -as [type])) {
                Add-Type 'using System; using System.Runtime.InteropServices; public static class BobineWindow { [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr window, int command); [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr window); }'
            }
            [BobineWindow]::ShowWindow($existing.MainWindowHandle, 9) | Out-Null
            [BobineWindow]::SetForegroundWindow($existing.MainWindowHandle) | Out-Null
            return
        }
    }
}
if ($hostStarted) { return }
Start-Process -FilePath $desktopPython -ArgumentList @(('"' + $desktopEntry + '"')) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
