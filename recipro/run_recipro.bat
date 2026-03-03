@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ==========================================================
:: Recipro Evolution - Windows Launcher (BAT)
:: - Detecta Python 3.10+
:: - Cria/usa venv em %PROJECT_DIR%\venv
:: - Instala dependências (na 1ª vez ou quando forçado)
:: - Sobe FastAPI com uvicorn em http://127.0.0.1:8000
:: - Opcional: restart automático (AUTO_RESTART=1)
:: ==========================================================

:: [CONFIG] Diretório do projeto (edite se necessário)
set "PROJECT_DIR=C:\Users\SABRINA\Desktop\github.com.br-codex-create-web-app-recipro-evolution\recipro"

:: [CONFIG] Nome do ambiente virtual
set "VENV_NAME=venv"

:: [CONFIG] Endpoint e app
set "APP_MODULE=main:app"
set "HOST=127.0.0.1"
set "PORT=8000"

:: [CONFIG] Reinício automático quando servidor cai (0=desligado, 1=ligado)
if "%AUTO_RESTART%"=="" set "AUTO_RESTART=0"

:: [CONFIG] Forçar reinstalação de dependências (0/1)
if "%FORCE_INSTALL%"=="" set "FORCE_INSTALL=0"

:: [CONFIG] Saída mais limpa do pip
set "PIP_FLAGS=--disable-pip-version-check --no-input --quiet"

:: Fallback: se PROJECT_DIR não existir, usa pasta do script
if not exist "%PROJECT_DIR%" (
  set "PROJECT_DIR=%~dp0"
)

for %%i in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fi"
set "VENV_DIR=%PROJECT_DIR%\%VENV_NAME%"
set "REQ_FILE=%PROJECT_DIR%\requirements.txt"
set "STAMP_FILE=%VENV_DIR%\.deps_installed"

cd /d "%PROJECT_DIR%" || goto :fatal

call :banner
call :detect_python || goto :fatal
call :setup_venv || goto :fatal
call :install_deps || goto :fatal
call :run_server
exit /b 0

:banner
echo ================================================
echo Recipro Evolution - Launcher Windows
echo Projeto: %PROJECT_DIR%
echo ================================================
exit /b 0

:detect_python
set "PY_CMD="
echo [1/4] Detectando Python 3.10+...

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
  echo [ERRO] Instale Python e marque "Add python.exe to PATH".
  exit /b 1
)

for /f "delims=" %%v in ('%PY_CMD% -c "import sys; print(sys.version.split()[0])"') do set "PY_VER=%%v"
echo [OK] Python selecionado: %PY_CMD% (versao %PY_VER%)
exit /b 0

:setup_venv
echo [2/4] Ativando ambiente...
if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo [INFO] Criando venv em "%VENV_DIR%"...
  %PY_CMD% -m venv "%VENV_DIR%" || exit /b 1
) else (
  echo [OK] venv ja existe.
)

call "%VENV_DIR%\Scripts\activate.bat" || exit /b 1
echo [OK] Ambiente ativo: %VENV_DIR%
exit /b 0

:install_deps
if not exist "%REQ_FILE%" (
  echo [ERRO] Arquivo requirements.txt nao encontrado em: %REQ_FILE%
  exit /b 1
)

echo [3/4] Verificando dependencias...
if "%FORCE_INSTALL%"=="1" del /f /q "%STAMP_FILE%" >nul 2>nul

if exist "%STAMP_FILE%" (
  echo [OK] Dependencias ja instaladas. (use FORCE_INSTALL=1 para reinstalar)
  exit /b 0
)

echo [INFO] Instalando dependencias...
python -m pip install %PIP_FLAGS% --upgrade pip || exit /b 1
python -m pip install %PIP_FLAGS% -r "%REQ_FILE%" || exit /b 1

echo ok> "%STAMP_FILE%"
echo [OK] Dependencias instaladas.
exit /b 0

:run_server
echo [4/4] Rodando servidor...
echo [OK] Endpoint ativo: http://%HOST%:%PORT%
echo [INFO] CTRL+C para parar.

:server_loop
python -m uvicorn %APP_MODULE% --host %HOST% --port %PORT% --reload
set "UVICORN_EXIT=%errorlevel%"

if "%AUTO_RESTART%"=="1" (
  echo [WARN] Servidor encerrou com codigo %UVICORN_EXIT%. Reiniciando em 2s...
  timeout /t 2 /nobreak >nul
  goto :server_loop
)

exit /b %UVICORN_EXIT%

:fatal
echo.
echo [FALHA] Nao foi possivel iniciar o Recipro Evolution.
exit /b 1
