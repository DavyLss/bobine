$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (!(Test-Path -LiteralPath $python)) { throw 'Lancer Installer.ps1 pour créer les environnements.' }
& $python -m pip install -r (Join-Path $PSScriptRoot 'requirements-desktop.txt') -c (Join-Path $PSScriptRoot 'requirements-lock.txt')
if ($LASTEXITCODE -ne 0) { throw 'Installation de la fenêtre Bobine interrompue.' }
& $python (Join-Path $PSScriptRoot 'studio/desktop.py') --check
if ($LASTEXITCODE -ne 0) { throw 'Installer Microsoft WebView2 Runtime depuis https://developer.microsoft.com/microsoft-edge/webview2/ puis relancer Installer-Fenetre.ps1.' }
Write-Host 'Fenêtre Bobine prête : moteur WebView2 indépendant du navigateur personnel.'
