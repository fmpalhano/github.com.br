@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ==============================================================
REM  Recipro Evolution - Launcher Oficial Windows (duplo clique)
REM ==============================================================
REM  O que este script faz:
REM  1) Detecta Python 3.10+
REM  2) Cria/ativa venv em .\venv
REM  3) Instala requirements (apenas quando necessário)
REM  4) Inicia uvicorn em http://127.0.0.1:8000 --reload
REM  5) Salva log completo em .\logs\run_YYYYMMDD_HHMMSS.log
REM
REM  Configurações rápidas:
REM    set FORCE_INSTALL=1    -> força reinstalar dependências
REM    set AUTO_RESTART=1     -> reinicia servidor automaticamente
REM ============================================================== 

REM [CONFIG] Diretório do projeto (por padrão: pasta do script)
set "PROJECT_DIR=%~dp0"
for %%i in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fi"

REM [CONFIG] Nome da virtualenv
set "VENV_NAME=venv"

REM [CONFIG] App/host/porta
set "APP_MODULE=main:app"
set "HOST=127.0.0.1"
set "PORT=8000"

REM [CONFIG] Flags opcionais
if "%FORCE_INSTALL%"=="" set "FORCE_INSTALL=0"
if "%AUTO_RESTART%"=="" set "AUTO_RESTART=0"

set "VENV_DIR=%PROJECT_DIR%\%VENV_NAME%"
set "REQ_FILE=%PROJECT_DIR%\requirements.txt"
set "STAMP_FILE=%VENV_DIR%\.deps_installed"
set "LOG_DIR=%PROJECT_DIR%\logs"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "TS=%%i"
set "LOG_FILE=%LOG_DIR%\run_%TS%.log"

cd /d "%PROJECT_DIR%" || goto :fatal

call :log "=============================================================="
call :log "Recipro Evolution - Inicializacao"
call :log "Projeto: %PROJECT_DIR%"
call :log "Log: %LOG_FILE%"
call :log "=============================================================="

echo [1/5] Detectando Python 3.10+...
call :detect_python || goto :fatal

echo [2/5] Preparando ambiente virtual...
call :prepare_venv || goto :fatal

echo [3/5] Instalando dependencias (se necessario)...
call :install_requirements || goto :fatal

echo [4/5] Validando imports criticos...
call :validate_imports || goto :fatal

echo [5/5] Rodando servidor...
call :run_server
exit /b 0

:detect_python
set "PY_CMD="

where py >nul 2>nul
if %errorlevel%==0 (
  py -3.14 -c "import sys" >nul 2>nul && set "PY_CMD=py -3.14"
  if not defined PY_CMD py -3.13 -c "import sys" >nul 2>nul && set "PY_CMD=py -3.13"
  if not defined PY_CMD py -3.12 -c "import sys" >nul 2>nul && set "PY_CMD=py -3.12"
  if not defined PY_CMD py -3.11 -c "import sys" >nul 2>nul && set "PY_CMD=py -3.11"
  if not defined PY_CMD py -3.10 -c "import sys" >nul 2>nul && set "PY_CMD=py -3.10"
)

if not defined PY_CMD (
  where python >nul 2>nul
  if %errorlevel%==0 set "PY_CMD=python"
)

if not defined PY_CMD (
  echo [ERRO] Python 3.10+ nao encontrado.
  call :log "[ERRO] Python 3.10+ nao encontrado."
  exit /b 1
)

for /f "delims=" %%v in ('%PY_CMD% -c "import sys; print(sys.version.split()[0])"') do set "PY_VER=%%v"

echo [OK] Python selecionado: %PY_CMD% (versao %PY_VER%)
call :log "[OK] Python selecionado: %PY_CMD% (versao %PY_VER%)"
exit /b 0

:prepare_venv
if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo [INFO] Criando venv em "%VENV_DIR%"...
  call :log "[INFO] Criando venv em %VENV_DIR%"
  %PY_CMD% -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
  if errorlevel 1 (
    call :log "[ERRO] Falha ao criar venv"
    exit /b 1
  )
) else (
  echo [OK] venv ja existe.
  call :log "[OK] venv ja existe"
)

call "%VENV_DIR%\Scripts\activate.bat" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log "[ERRO] Falha ao ativar venv"
  exit /b 1
)

echo [OK] Ambiente ativo: %VENV_DIR%
call :log "[OK] Ambiente ativo: %VENV_DIR%"
exit /b 0

:install_requirements
if not exist "%REQ_FILE%" (
  echo [ERRO] requirements.txt nao encontrado.
  call :log "[ERRO] requirements.txt nao encontrado em %REQ_FILE%"
  exit /b 1
)

if "%FORCE_INSTALL%"=="1" del /f /q "%STAMP_FILE%" >nul 2>nul

if exist "%STAMP_FILE%" (
  echo [OK] Dependencias ja instaladas.
  call :log "[OK] Dependencias ja instaladas (STAMP_FILE presente)"
  exit /b 0
)

echo [INFO] Instalando dependencias... (primeira execucao pode demorar)
call :log "[INFO] Instalando dependencias"
python -m pip install --disable-pip-version-check --no-input --upgrade pip >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log "[ERRO] Falha no upgrade do pip"
  exit /b 1
)

python -m pip install --disable-pip-version-check --no-input -r "%REQ_FILE%" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log "[ERRO] Falha ao instalar requirements"
  exit /b 1
)

echo ok> "%STAMP_FILE%"
echo [OK] Dependencias instaladas com sucesso.
call :log "[OK] Dependencias instaladas"
exit /b 0

:validate_imports
python -c "import fastapi,uvicorn,pandas,spacy,textblob,sqlalchemy,reportlab; import main; print('IMPORT_OK')" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERRO] Falha ao importar modulos da aplicacao.
  call :log "[ERRO] Falha ao importar modulos da aplicacao"
  exit /b 1
)

echo [OK] Imports criticos validados.
call :log "[OK] Imports criticos validados"
exit /b 0

:run_server
echo [OK] Endpoint: http://%HOST%:%PORT%
echo [INFO] Para parar: CTRL+C
call :log "[OK] Endpoint: http://%HOST%:%PORT%"

:server_loop
python -m uvicorn %APP_MODULE% --host %HOST% --port %PORT% --reload >> "%LOG_FILE%" 2>&1
set "UV_EXIT=%errorlevel%"
call :log "[WARN] Uvicorn encerrou com codigo %UV_EXIT%"

if "%AUTO_RESTART%"=="1" (
  echo [WARN] Servidor caiu (codigo %UV_EXIT%). Reiniciando em 2s...
  timeout /t 2 /nobreak >nul
  goto :server_loop
)

exit /b %UV_EXIT%

:log
echo %~1
echo %~1>> "%LOG_FILE%"
exit /b 0

:fatal
echo.
echo [FALHA] Nao foi possivel iniciar o Recipro Evolution.
echo [FALHA] Veja o log: %LOG_FILE%
if defined LOG_FILE echo [FALHA] Inicializacao interrompida>> "%LOG_FILE%"
pause
exit /b 1
