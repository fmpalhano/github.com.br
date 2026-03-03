@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Recipro Evolution - Windows launcher (ASCII/CRLF-safe)
REM Double click to run

set "PROJECT_DIR=%~dp0"
for %%i in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fi"
set "VENV_NAME=venv"
set "VENV_DIR=%PROJECT_DIR%\%VENV_NAME%"
set "REQ_FILE=%PROJECT_DIR%\requirements.txt"
set "STAMP_FILE=%VENV_DIR%\.deps_installed"
set "HOST=127.0.0.1"
set "PORT=8000"
set "APP_MODULE=main:app"
if "%FORCE_INSTALL%"=="" set "FORCE_INSTALL=0"
if "%AUTO_RESTART%"=="" set "AUTO_RESTART=0"

set "LOG_DIR=%PROJECT_DIR%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "TS=%%i"
set "LOG_FILE=%LOG_DIR%\run_%TS%.log"

cd /d "%PROJECT_DIR%" || goto fatal

echo ============================================== 
echo Recipro Evolution launcher
echo Project: %PROJECT_DIR%
echo Log: %LOG_FILE%
echo ============================================== 
echo ============================================== >> "%LOG_FILE%"
echo Recipro Evolution launcher>> "%LOG_FILE%"
echo Project: %PROJECT_DIR%>> "%LOG_FILE%"
echo ============================================== >> "%LOG_FILE%"

echo [1/5] Detecting Python 3.10+ ...
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
  echo [ERROR] Python 3.10+ not found.
  echo [ERROR] Python 3.10+ not found.>> "%LOG_FILE%"
  goto fatal
)
for /f "delims=" %%v in ('%PY_CMD% -c "import sys; print(sys.version.split()[0])"') do set "PY_VER=%%v"
echo [OK] Python: %PY_CMD% (%PY_VER%)
echo [OK] Python: %PY_CMD% (%PY_VER%)>> "%LOG_FILE%"

echo [2/5] Preparing virtual environment ...
if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo [INFO] Creating venv ...
  %PY_CMD% -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
  if errorlevel 1 goto fatal
) else (
  echo [OK] venv already exists.
)
call "%VENV_DIR%\Scripts\activate.bat" >> "%LOG_FILE%" 2>&1
if errorlevel 1 goto fatal
echo [OK] venv active: %VENV_DIR%

echo [3/5] Installing dependencies (if needed) ...
if "%FORCE_INSTALL%"=="1" del /f /q "%STAMP_FILE%" >nul 2>nul
if exist "%STAMP_FILE%" (
  echo [OK] Dependencies already installed.
) else (
  echo [INFO] Installing dependencies - first run may take some time ...
  python -m pip install --disable-pip-version-check --no-input --upgrade pip >> "%LOG_FILE%" 2>&1
  if errorlevel 1 goto fatal
  python -m pip install --disable-pip-version-check --no-input -r "%REQ_FILE%" >> "%LOG_FILE%" 2>&1
  if errorlevel 1 goto fatal
  echo ok> "%STAMP_FILE%"
  echo [OK] Dependencies installed.
)

echo [4/5] Validating runtime imports ...
python -c "import fastapi,uvicorn,pandas,spacy,textblob,sqlalchemy,reportlab; import main; print('IMPORT_OK')" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] Import validation failed.
  echo [ERROR] Import validation failed.>> "%LOG_FILE%"
  goto fatal
)
echo [OK] Import validation passed.

echo [5/5] Starting server ...
echo [OK] Endpoint: http://%HOST%:%PORT%
echo [INFO] Press CTRL+C to stop.
:server_loop
python -m uvicorn %APP_MODULE% --host %HOST% --port %PORT% --reload >> "%LOG_FILE%" 2>&1
set "UV_EXIT=%errorlevel%"
echo [WARN] Uvicorn exited with code %UV_EXIT%>> "%LOG_FILE%"
if "%AUTO_RESTART%"=="1" (
  echo [WARN] Server stopped, code %UV_EXIT%. Restarting in 2s ...
  timeout /t 2 /nobreak >nul
  goto server_loop
)
exit /b %UV_EXIT%

:fatal
echo.
echo [FAILED] Could not start Recipro Evolution.
echo [FAILED] Check log: %LOG_FILE%
if defined LOG_FILE echo [FAILED] Startup interrupted>> "%LOG_FILE%"
pause
exit /b 1
