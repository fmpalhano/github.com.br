<#
Recipro Evolution - Launcher PowerShell
- Detecta Python 3.10+
- Cria/ativa venv
- Instala requirements
- Sobe uvicorn com reload
Uso:
  powershell -ExecutionPolicy Bypass -File .\run_recipro.ps1
  $env:FORCE_INSTALL='1'; .\run_recipro.ps1
  $env:AUTO_RESTART='1'; .\run_recipro.ps1
#>

$ProjectDir = 'C:\Users\SABRINA\Desktop\github.com.br-codex-create-web-app-recipro-evolution\recipro'
$VenvName = 'venv'
$HostName = '127.0.0.1'
$Port = 8000
$AppModule = 'main:app'
$AutoRestart = [int]($env:AUTO_RESTART ?? '0')
$ForceInstall = [int]($env:FORCE_INSTALL ?? '0')

if (-not (Test-Path $ProjectDir)) { $ProjectDir = $PSScriptRoot }
$ProjectDir = (Resolve-Path $ProjectDir).Path
$VenvDir = Join-Path $ProjectDir $VenvName
$ReqFile = Join-Path $ProjectDir 'requirements.txt'
$StampFile = Join-Path $VenvDir '.deps_installed'

function Write-Step($msg) { Write-Host $msg -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host $msg -ForegroundColor Green }
function Write-Err($msg) { Write-Host $msg -ForegroundColor Red }

function Get-PythonCommand {
    $candidates = @('py -3.14','py -3.13','py -3.12','py -3.11','py -3.10','python')
    foreach ($cmd in $candidates) {
        try {
            & cmd /c "$cmd -c \"import sys\"" | Out-Null
            if ($LASTEXITCODE -eq 0) { return $cmd }
        } catch {}
    }
    return $null
}

Set-Location $ProjectDir
Write-Host '==============================================='
Write-Host 'Recipro Evolution - Launcher PowerShell'
Write-Host "Projeto: $ProjectDir"
Write-Host '==============================================='

Write-Step '[1/4] Detectando Python 3.10+...'
$pyCmd = Get-PythonCommand
if (-not $pyCmd) { Write-Err 'Python 3.10+ não encontrado.'; exit 1 }
$pyVer = (& cmd /c "$pyCmd -c \"import sys; print(sys.version.split()[0])\"").Trim()
Write-Ok "[OK] Python selecionado: $pyCmd (versão $pyVer)"

Write-Step '[2/4] Ativando ambiente...'
if (-not (Test-Path (Join-Path $VenvDir 'Scripts\python.exe'))) {
    Write-Host "[INFO] Criando venv em $VenvDir ..."
    & cmd /c "$pyCmd -m venv \"$VenvDir\""
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Ok '[OK] venv já existe.'
}

$env:VIRTUAL_ENV = $VenvDir
$env:PATH = (Join-Path $VenvDir 'Scripts') + ';' + $env:PATH
Write-Ok "[OK] Ambiente ativo: $VenvDir"

Write-Step '[3/4] Verificando dependências...'
if (-not (Test-Path $ReqFile)) { Write-Err "requirements.txt não encontrado em $ReqFile"; exit 1 }
if ($ForceInstall -eq 1 -and (Test-Path $StampFile)) { Remove-Item $StampFile -Force }

if (-not (Test-Path $StampFile)) {
    Write-Host '[INFO] Instalando dependências...'
    python -m pip install --disable-pip-version-check --no-input --quiet --upgrade pip
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    python -m pip install --disable-pip-version-check --no-input --quiet -r $ReqFile
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Set-Content -Path $StampFile -Value 'ok'
    Write-Ok '[OK] Dependências instaladas.'
} else {
    Write-Ok '[OK] Dependências já instaladas.'
}

Write-Step '[4/4] Rodando servidor...'
Write-Ok "[OK] Endpoint ativo: http://$HostName`:$Port"
Write-Host '[INFO] CTRL+C para parar.'

while ($true) {
    python -m uvicorn $AppModule --host $HostName --port $Port --reload
    $code = $LASTEXITCODE
    if ($AutoRestart -ne 1) { exit $code }
    Write-Host "[WARN] Servidor caiu (code=$code). Reiniciando em 2s..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}
