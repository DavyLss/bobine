$ErrorActionPreference = 'Stop'
$desktop = [Environment]::GetFolderPath('DesktopDirectory')
if (!$desktop -or !(Test-Path -LiteralPath $desktop -PathType Container)) { throw 'Le Bureau utilisateur est introuvable.' }
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut((Join-Path $desktop 'Bobine.lnk'))
$shortcut.TargetPath = Join-Path $env:SystemRoot 'System32/WindowsPowerShell/v1.0/powershell.exe'
$shortcut.Arguments = '-NoProfile -WindowStyle Hidden -File "' + (Join-Path $PSScriptRoot 'Lancer-Studio.ps1') + '"'
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.IconLocation = (Join-Path $PSScriptRoot 'studio/static/brand/favicon.ico') + ',0'
$shortcut.Description = 'Bobine - Vos idées prennent vie, image après image.'
$shortcut.WindowStyle = 7
$shortcut.Save()
Write-Host 'Raccourci Bobine créé sur le Bureau.'
