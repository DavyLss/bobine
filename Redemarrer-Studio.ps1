# Restart only this studio when no generation or transfer is active.
$ErrorActionPreference = 'Stop'
$localConfigPath = Join-Path $PSScriptRoot '.local/config.json'
$localConfig = if (Test-Path $localConfigPath) { Get-Content -Raw $localConfigPath | ConvertFrom-Json } else { $null }
$studioPort = if ($env:STUDIO_PORT) { [int]$env:STUDIO_PORT } elseif ($localConfig -and $localConfig.STUDIO_PORT) { [int]$localConfig.STUDIO_PORT } else { 8510 }
$listener = Get-NetTCPConnection -LocalPort $studioPort -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    $state = Invoke-RestMethod "http://127.0.0.1:$studioPort/api/state" -TimeoutSec 5
    $active = @($state.jobs | Where-Object { $_.status -in @('queued','running') -or $_.publication.status -in @('queued','preparing','sending','uploading') })
    if ($active.Count) { throw 'Une génération ou un transfert est actif. Attendre sa fin avant le redémarrage.' }
    $expected = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'studio/server.py')).Replace('\','/').ToLowerInvariant()
    foreach ($processId in @($listener.OwningProcess | Select-Object -Unique)) {
        $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId=$processId"
        $line = ([string]$processInfo.CommandLine).Replace('\','/').ToLowerInvariant()
        if (!$line.Contains($expected)) { throw "Le port $studioPort appartient à un autre processus. Aucun arrêt effectué." }
        $studioProcess = Get-Process -Id $processId -ErrorAction Stop
        Stop-Process -InputObject $studioProcess -ErrorAction Stop
        if (!$studioProcess.WaitForExit(10000)) { throw "Le serveur précédent ne s'est pas arrêté à temps." }
    }
}
& (Join-Path $PSScriptRoot 'Lancer-Studio.ps1')
