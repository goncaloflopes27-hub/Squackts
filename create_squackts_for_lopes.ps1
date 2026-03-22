<#
  Salve como: create_squackts_for_lopes.ps1
  Exemplo de execução:
    PowerShell -NoProfile -ExecutionPolicy Bypass -File .\create_squackts_for_lopes.ps1
    PowerShell -NoProfile -ExecutionPolicy Bypass -File .\create_squackts_for_lopes.ps1 -ForceRecreate
#>

param(
    [string]$ProjectFolder = "C:\Users\lopes\Downloads\Squackts",
    [string]$TemplateSource = "",            # opcional: caminho para a pasta do template; se vazio usa a pasta do script ou diretório atual
    [switch]$ForceRecreate,
    [switch]$SkipVenv,
    [switch]$SkipShortcut
)

$ErrorActionPreference = "Stop"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "SquackTS Enterprise.lnk"
$LogFile = Join-Path $env:TEMP "create_squackts_log.txt"

function Log($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $msg"
    $line | Out-File -FilePath $LogFile -Append -Encoding UTF8
    Write-Host $msg
}

function Ensure-Dir([string]$Path) {
    if (-not (Test-Path $Path)) { New-Item -ItemType Directory -Path $Path -Force | Out-Null }
}

function Get-PythonLauncher {
    if (Get-Command py -ErrorAction SilentlyContinue) { return "py" }
    if (Get-Command python -ErrorAction SilentlyContinue) { return "python" }
    throw "Python 3+ não encontrado no PATH."
}

# Determina a pasta do template de forma segura
if ($TemplateSource -and $TemplateSource.Trim() -ne "") {
    $source = $TemplateSource
} elseif ($PSScriptRoot -and $PSScriptRoot.Trim() -ne "") {
    $source = $PSScriptRoot
} elseif ($PSCommandPath -and $PSCommandPath.Trim() -ne "") {
    $source = Split-Path -Parent $PSCommandPath
} else {
    $source = (Get-Location).Path
}
Log "Template source: $source"
Log "Project folder: $ProjectFolder"
Log "Log file: $LogFile"

try {
    $sourceResolved = (Resolve-Path -LiteralPath $source).Path
    $projectResolved = $null
    if (Test-Path $ProjectFolder) {
        $projectResolved = (Resolve-Path -LiteralPath $ProjectFolder).Path
    }
    if ($projectResolved -and ($sourceResolved -eq $projectResolved)) {
        throw "TemplateSource e ProjectFolder não podem ser o mesmo caminho."
    }

    if ($ForceRecreate -and (Test-Path $ProjectFolder)) {
        Log "Removendo pasta existente: $ProjectFolder"
        Remove-Item -Recurse -Force -Path $ProjectFolder
    }

    Ensure-Dir $ProjectFolder

    # Copia template do repositório para a pasta de destino (exclui .git e venv)
    Get-ChildItem -Path $source -Force |
        Where-Object { $_.Name -notin @('.git', 'venv', '__pycache__') } |
        ForEach-Object {
            $target = Join-Path $ProjectFolder $_.Name
            if ($_.PSIsContainer) {
                Copy-Item -Path $_.FullName -Destination $target -Recurse -Force
                Log "Copiado diretório: $($_.FullName) -> $target"
            } else {
                Copy-Item -Path $_.FullName -Destination $target -Force
                Log "Copiado ficheiro: $($_.FullName) -> $target"
            }
        }

    if (-not $SkipVenv) {
        Push-Location $ProjectFolder
        try {
            $launcher = Get-PythonLauncher
            Log "Usando launcher Python: $launcher"

            if (-not (Test-Path ".\venv\Scripts\python.exe")) {
                Log "Criando virtualenv..."
                if ($launcher -eq "py") { & py -3 -m venv venv } else { & python -m venv venv }
            } else {
                Log "venv já existe, pulando criação."
            }

            $venvPy = Join-Path $ProjectFolder "venv\Scripts\python.exe"
            if (-not (Test-Path $venvPy)) {
                throw "Python do venv não encontrado em $venvPy"
            }

            Log "Atualizando pip e instalando dependências (se existir requirements.txt)..."
            & $venvPy -m pip install --upgrade pip setuptools wheel | Out-Null
            if (Test-Path ".\requirements.txt") {
                & $venvPy -m pip install -r requirements.txt
                Log "Dependências instaladas."
            } else {
                Log "Aviso: requirements.txt não encontrado em $ProjectFolder"
            }
        }
        finally {
            Pop-Location
        }
    } else {
        Log "SkipVenv ativado: não cria venv nem instala dependências."
    }

    if (-not $SkipShortcut) {
        $targetBat = Join-Path $ProjectFolder "Iniciar App.bat"
        if (-not (Test-Path $targetBat)) {
            Log "Criando Iniciar App.bat..."
            $batContent = "@echo off`ncd /d `"" + $ProjectFolder + "`nif not exist venv\Scripts\python.exe (`n  py -3 -m venv venv`n)`nvenv\Scripts\python.exe -m pip install -r requirements.txt`nvenv\Scripts\python.exe app.py"
            $batContent | Out-File -FilePath $targetBat -Encoding ASCII
        } else {
            Log "Iniciar App.bat já existe."
        }

        try {
            $wsh = New-Object -ComObject WScript.Shell
            $shortcut = $wsh.CreateShortcut($ShortcutPath)
            $shortcut.TargetPath = $targetBat
            $shortcut.WorkingDirectory = $ProjectFolder
            $shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,1"
            $shortcut.Save()
            Log "Atalho criado no Desktop: $ShortcutPath"
        } catch {
            Log "Aviso: não foi possível criar atalho (pode ser permissão). Erro: $($_.Exception.Message)"
        }
    } else {
        Log "SkipShortcut ativado: não cria atalho."
    }

    Log "✅ SquackTS Enterprise criado em: $ProjectFolder"
    Write-Host ""
    Write-Host "✅ SquackTS Enterprise criado em: $ProjectFolder" -ForegroundColor Green
    Write-Host "Log gravado em: $LogFile"
    Read-Host "Prima Enter para fechar"
    exit 0

} catch {
    $errFile = Join-Path $env:TEMP "create_squackts_error.txt"
    $_ | Out-File -FilePath $errFile -Append -Encoding UTF8
    Log "ERRO: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Ocorreu um erro. Detalhes gravados em: $errFile" -ForegroundColor Red
    Write-Host "Verifique também o log: $LogFile"
    Read-Host "Prima Enter para fechar"
    exit 1
}
