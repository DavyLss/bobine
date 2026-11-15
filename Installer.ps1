param([string]$Python = 'py', [switch]$SkipModels)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
function Run-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Échec de $Executable (code $LASTEXITCODE)" }
}
$prefix = @()
if ($Python -eq 'py') { $prefix = @('-3.11') }
Run-Checked $Python ($prefix + @('-c', 'import sys; assert sys.version_info[:2] == (3,11), "Python 3.11 requis"'))
foreach ($environment in @('.venv', '.venv-voice')) {
    if (!(Test-Path "$environment/Scripts/python.exe")) {
        Run-Checked $Python ($prefix + @('-m', 'venv', $environment))
    }
}
Run-Checked '.venv/Scripts/python.exe' @('-m','pip','install','-r','requirements.txt','-c','requirements-lock.txt')
Run-Checked '.venv-voice/Scripts/python.exe' @('-m','pip','install','torch==2.6.0','torchaudio==2.6.0','--index-url','https://download.pytorch.org/whl/cpu')
Run-Checked '.venv-voice/Scripts/python.exe' @('-m','pip','install','-r','requirements-voice.txt')
if (!$SkipModels) {
    if (!(Get-Command ollama -ErrorAction SilentlyContinue)) { throw 'Installer Ollama depuis https://ollama.com/download puis relancer Installer.ps1.' }
    Run-Checked '.venv/Scripts/python.exe' @('scripts/download_models.py')
    Run-Checked 'ollama' @('pull','qwen3:4b')
}
Write-Host 'Installation terminée. Lancer : .\Lancer-Studio.ps1'
