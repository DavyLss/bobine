# Isolated Windows checks: no service, browser or real taskkill is launched.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
$sourceRepo = Split-Path $PSScriptRoot -Parent
$tempRoot = [IO.Path]::GetTempPath()
$repo = Join-Path $tempRoot ('bobine-desktop-check-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path (Join-Path $repo '.venv/Scripts') -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $repo '.venv/Scripts/python.exe') | Out-Null
New-Item -ItemType File -Path (Join-Path $repo '.venv/Scripts/pythonw.exe') | Out-Null
foreach ($name in @('Lancer-Studio.ps1','Bobine-Tray.ps1')) { Copy-Item -LiteralPath (Join-Path $sourceRepo $name) -Destination $repo }
$global:BobineTestLaunches = @()
$global:BobineTestKilled = @()
function Start-Process { param($FilePath,$ArgumentList,$WindowStyle) $global:BobineTestLaunches += @{File=$FilePath;Arguments=$ArgumentList} }
function Invoke-RestMethod { param($Uri,$TimeoutSec) return @{jobs=@()} }
function Get-CimInstance { param($ClassName,$Filter) return @() }
try {
    & (Join-Path $repo 'Lancer-Studio.ps1') -SansZone
    if ($global:BobineTestLaunches.Count -ne 1 -or $global:BobineTestLaunches[0].File -notlike '*pythonw.exe') { throw 'Embedded host was not selected.' }
    if (($global:BobineTestLaunches[0].Arguments -join ' ') -notlike '*studio*desktop.py*') { throw 'Embedded entry point missing.' }
    $global:BobineTestLaunches = @()
    & (Join-Path $repo 'Lancer-Studio.ps1')
    if (($global:BobineTestLaunches[0].Arguments -join ' ') -notlike '*-STA*Bobine-Tray.ps1*') { throw 'Tray delegation missing.' }
    $global:BobineTestLaunches = @()
    & (Join-Path $repo 'Lancer-Studio.ps1') -Navigateur
    if ($global:BobineTestLaunches[0].File -notlike 'http://127.0.0.1:*') { throw 'Explicit browser fallback failed.' }

    # Real notification callbacks must work without ambient script variables.
    $trayAst = [Management.Automation.Language.Parser]::ParseFile((Join-Path $repo 'Bobine-Tray.ps1'),[ref]$null,[ref]$null)
    $openFunction = $trayAst.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Open-Bobine'},$true)
    . ([ScriptBlock]::Create($openFunction.Extent.Text))
    $marker = Join-Path $repo 'opened.txt'
    Set-Content -LiteralPath (Join-Path $repo 'Lancer-Studio.ps1') -Encoding UTF8 -Value 'param([switch]$SansZone) [IO.File]::AppendAllText((Join-Path $PSScriptRoot "opened.txt"), "opened`n")'
    $script:root = $null
    $script:url = $null
    $context = @{Root=$repo;Port=8511;Url='http://127.0.0.1:8511';Open=${function:Open-Bobine};OpenEvent=[Threading.EventWaitHandle]::new($false,[Threading.EventResetMode]::AutoReset)}
    foreach ($name in @('openHandler','reopenHandler')) {
        $assignment = $trayAst.Find({param($node) $node -is [Management.Automation.Language.AssignmentStatementAst] -and $node.Left.Extent.Text -eq ('$' + $name)},$true)
        . ([ScriptBlock]::Create($assignment.Extent.Text))
    }
    $menuItem = [Windows.Forms.ToolStripMenuItem]::new('Open')
    try {
        $menuItem.Tag = $context
        $menuItem.add_Click($openHandler)
        $menuItem.PerformClick()
        $context.OpenEvent.Set() | Out-Null
        & $reopenHandler
        & $reopenHandler # Auto-reset: a repeated timer tick must not reopen twice.
        if (@(Get-Content -LiteralPath $marker).Count -ne 2) { throw 'Notification click or shortcut reopen failed without script context.' }
    } finally { $menuItem.Dispose(); $context.OpenEvent.Dispose() }

    # Exercise the real quit handler against fake process snapshots.
    $script:root = $repo
    $script:url = 'http://127.0.0.1:8511'
    $studioPort = 8511
    $serverPath = Join-Path $repo 'studio/server.py'
    $desktopPath = Join-Path $repo 'studio/desktop.py'
    function Get-NetTCPConnection { param($LocalPort,$State,$ErrorAction) return @{OwningProcess=501} }
    function Get-CimInstance {
        param($ClassName,$Filter)
        if ($Filter -eq 'ProcessId=501') { return @{ProcessId=501;CommandLine=('python "' + $serverPath + '"')} }
        return @(@{ProcessId=502;ParentProcessId=1;CommandLine=('pythonw "' + $desktopPath + '"')}, @{ProcessId=504;ParentProcessId=502;CommandLine=('pythonw "' + $desktopPath + '"')}, @{ProcessId=503;CommandLine='pythonw personal-app.py'})
    }
    function Invoke-TestTaskkill { $global:BobineTestKilled += $args[1]; $global:LASTEXITCODE=0 }
    function Join-Path {
        param($Path,$ChildPath)
        if ($ChildPath -eq 'System32/taskkill.exe') { return 'Invoke-TestTaskkill' }
        Microsoft.PowerShell.Management\Join-Path $Path $ChildPath
    }
    $ast = [Management.Automation.Language.Parser]::ParseFile((Join-Path $repo 'Bobine-Tray.ps1'),[ref]$null,[ref]$null)
    $handler = $ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Stop-Bobine'},$true)
    . ([ScriptBlock]::Create($handler.Extent.Text))
    Stop-Bobine -Context @{Root=$repo;Port=8511;Url='http://127.0.0.1:8511'}
    if (($global:BobineTestKilled -join ',') -ne '501,502') { throw 'Quit must stop only this server and dedicated profile.' }
    Write-Host 'OK: embedded host, notification click and shortcut reopen without script context, browser fallback and scoped shutdown.'
} finally {
    $resolved = [IO.Path]::GetFullPath($repo)
    if ((Split-Path $resolved -Parent).TrimEnd('\') -ne $tempRoot.TrimEnd('\') -or (Split-Path $resolved -Leaf) -notlike 'bobine-desktop-check-*') { throw 'Unsafe test cleanup path.' }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
