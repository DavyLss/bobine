$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
$script:root = $PSScriptRoot
$localConfigPath = Join-Path $script:root '.local/config.json'
$localConfig = if (Test-Path -LiteralPath $localConfigPath) { Get-Content -Raw -LiteralPath $localConfigPath | ConvertFrom-Json } else { $null }
$studioPort = if ($env:STUDIO_PORT) { [int]$env:STUDIO_PORT } elseif ($localConfig -and $localConfig.STUDIO_PORT) { [int]$localConfig.STUDIO_PORT } else { 8510 }
$script:url = "http://127.0.0.1:$studioPort"
$sha = [Security.Cryptography.SHA256]::Create()
try { $instance = [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes(($script:root.ToLowerInvariant() + ':' + $studioPort)))).Replace('-', '').Substring(0,24) } finally { $sha.Dispose() }
$mutex = [Threading.Mutex]::new($false, ('Local\Bobine-' + $instance))
$ownsMutex = $false
try { $ownsMutex = $mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $ownsMutex = $true }
$openEvent = [Threading.EventWaitHandle]::new($false, [Threading.EventResetMode]::AutoReset, ('Local\BobineOpen-' + $instance))
if (!$ownsMutex) { $openEvent.Set() | Out-Null; $openEvent.Dispose(); $mutex.Dispose(); exit }
function Open-Bobine {
    try {
        $options = @{ SansZone = $true }
        & (Join-Path $script:root 'Lancer-Studio.ps1') @options
    } catch { [Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Bobine', 'OK', 'Error') | Out-Null }
}
function Stop-Bobine {
    try {
        $listener = Get-NetTCPConnection -LocalPort $studioPort -State Listen -ErrorAction SilentlyContinue
        $expected = [IO.Path]::GetFullPath((Join-Path $script:root 'studio/server.py')).Replace('\','/').ToLowerInvariant()
        $serverProcesses = @()
        foreach ($processId in @($listener.OwningProcess | Select-Object -Unique)) {
            if (!$processId) { continue }
            $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId=$processId"
            if (!([string]$processInfo.CommandLine).Replace('\','/').ToLowerInvariant().Contains($expected)) { throw 'Le port appartient à un autre programme. Aucun arrêt effectué.' }
            $serverProcesses += $processInfo
        }
        if ($serverProcesses.Count) {
            $state = Invoke-RestMethod "$script:url/api/state" -TimeoutSec 5
            $active = @($state.jobs | Where-Object { $_.status -eq 'running' -or $_.publication.status -in @('queued','preparing','sending','uploading') })
            if ($active.Count) {
                $answer = [Windows.Forms.MessageBox]::Show('Une génération ou un envoi est en cours. Quitter interrompra ces traitements. Une publication déjà acceptée par un réseau peut continuer. Quitter quand même ?', 'Quitter Bobine', 'YesNo', 'Warning', 'Button2')
                if ($answer -ne 'Yes') { return }
            }
        }
        foreach ($processInfo in $serverProcesses) {
            & (Join-Path $env:SystemRoot 'System32/taskkill.exe') /PID $processInfo.ProcessId /T /F | Out-Null
            if ($LASTEXITCODE -ne 0) { throw "Impossible d’arrêter le serveur. L’icône reste disponible." }
        }
        # Only Bobine's embedded host; never terminate a personal browser.
        $desktopKey = [IO.Path]::GetFullPath((Join-Path $script:root 'studio/desktop.py')).Replace('\','/').ToLowerInvariant()
        $desktopProcesses = @(Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" | Where-Object { ([string]$_.CommandLine).Replace('\','/').ToLowerInvariant().Contains($desktopKey) })
        foreach ($processInfo in $desktopProcesses) {
            if ($desktopProcesses.ProcessId -contains $processInfo.ParentProcessId) { continue }
            & (Join-Path $env:SystemRoot 'System32/taskkill.exe') /PID $processInfo.ProcessId /T /F | Out-Null
        }
        [Windows.Forms.Application]::ExitThread()
    } catch { [Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Bobine', 'OK', 'Error') | Out-Null }
}
$tray = [Windows.Forms.NotifyIcon]::new()
$icon = [Drawing.Icon]::new((Join-Path $script:root 'studio/static/brand/favicon.ico'))
$tray.Icon = $icon
$tray.Text = 'Bobine - actif en arrière-plan'
$menu = [Windows.Forms.ContextMenuStrip]::new()
$openItem = $menu.Items.Add('Ouvrir Bobine')
$openItem.add_Click({ Open-Bobine })
$menu.Items.Add([Windows.Forms.ToolStripSeparator]::new()) | Out-Null
$quitItem = $menu.Items.Add('Quitter Bobine')
$quitItem.add_Click({ Stop-Bobine })
$tray.ContextMenuStrip = $menu
$tray.add_DoubleClick({ Open-Bobine })
$timer = [Windows.Forms.Timer]::new()
$timer.Interval = 500
$timer.add_Tick({ if ($openEvent.WaitOne(0)) { Open-Bobine } })
try {
    $tray.Visible = $true
    $timer.Start()
    Open-Bobine
    [Windows.Forms.Application]::Run()
} finally {
    $timer.Stop(); $timer.Dispose()
    $tray.Visible = $false; $tray.Dispose(); $menu.Dispose(); $icon.Dispose()
    $openEvent.Dispose(); $mutex.ReleaseMutex(); $mutex.Dispose()
}
