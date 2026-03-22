param(
    [string]$ProjectFolder = (Join-Path $env:USERPROFILE "SquackTS_Enterprise"),
    [switch]$ForceRecreate,
    [switch]$SkipVenv,
    [switch]$SkipShortcut
)

$ErrorActionPreference = "Stop"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "SquackTS Enterprise.lnk"

function Ensure-Dir([string]$Path) {
    if (-not (Test-Path $Path)) { New-Item -ItemType Directory -Path $Path -Force | Out-Null }
}

function Get-PythonLauncher {
    if (Get-Command py -ErrorAction SilentlyContinue) { return "py" }
    if (Get-Command python -ErrorAction SilentlyContinue) { return "python" }
    throw "Python 3.11+ não encontrado no PATH."
}

if ($ForceRecreate -and (Test-Path $ProjectFolder)) {
    Remove-Item -Recurse -Force -Path $ProjectFolder
}
Ensure-Dir $ProjectFolder

# Copia template do repositório para a pasta de destino (exclui .git e venv)
$source = Split-Path -Parent $PSCommandPath
Get-ChildItem -Path $source -Force |
    Where-Object { $_.Name -notin @('.git', 'venv', '__pycache__') } |
    ForEach-Object {
        $target = Join-Path $ProjectFolder $_.Name
        if ($_.PSIsContainer) {
            Copy-Item -Path $_.FullName -Destination $target -Recurse -Force
        } else {
            Copy-Item -Path $_.FullName -Destination $target -Force
        }
    }

if (-not $SkipVenv) {
    Push-Location $ProjectFolder
    $launcher = Get-PythonLauncher
    if (-not (Test-Path ".\venv\Scripts\python.exe")) {
        if ($launcher -eq "py") { & py -3 -m venv venv } else { & python -m venv venv }
    }
    $venvPy = Join-Path $ProjectFolder "venv\Scripts\python.exe"
    & $venvPy -m pip install --upgrade pip setuptools wheel
    & $venvPy -m pip install -r requirements.txt
    Pop-Location
}

if (-not $SkipShortcut) {
    $targetBat = Join-Path $ProjectFolder "Iniciar App.bat"
    $wsh = New-Object -ComObject WScript.Shell
    $shortcut = $wsh.CreateShortcut($ShortcutPath)
    $shortcut.TargetPath = $targetBat
    $shortcut.WorkingDirectory = $ProjectFolder
    $shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,1"
    $shortcut.Save()
}

Write-Host "✅ SquackTS Enterprise criado em: $ProjectFolder" -ForegroundColor Green
