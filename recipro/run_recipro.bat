@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

if not exist "logs" mkdir logs
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set LOGFILE=logs\run_!TS!.log

echo [Recipro Evolution] Iniciando... > "!LOGFILE!"
echo Diretório: %CD%>> "!LOGFILE!"
echo Timestamp: !TS!>> "!LOGFILE!"

echo.
echo [INFO] Log desta execução: !LOGFILE!
echo [INFO] Se algo falhar, envie este arquivo.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set PY_CMD=py -3.11
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PY_CMD=python
    ) else (
        echo [ERRO] Python nao encontrado no PATH.
        echo [ERRO] Instale Python 3.11 e marque "Add python.exe to PATH".
        echo [ERRO] Python nao encontrado no PATH.>> "!LOGFILE!"
        pause
        exit /b 1
    )
)

echo [INFO] Python selecionado: !PY_CMD!
echo [INFO] Python selecionado: !PY_CMD!>> "!LOGFILE!"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Criando ambiente virtual... 
    echo [INFO] Criando ambiente virtual...>> "!LOGFILE!"
    !PY_CMD! -m venv .venv >> "!LOGFILE!" 2>&1
    if errorlevel 1 goto :fail
)

call ".venv\Scripts\activate" >> "!LOGFILE!" 2>&1
if errorlevel 1 goto :fail

python -m pip install --upgrade pip >> "!LOGFILE!" 2>&1
if errorlevel 1 goto :fail

python -m pip install -r requirements.txt >> "!LOGFILE!" 2>&1
if errorlevel 1 goto :fail

for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /R /C:"IPv4"') do (
    set IP=%%A
    goto :foundip
)
:foundip
set IP=!IP: =!
if "!IP!"=="" set IP=127.0.0.1

echo.>> "!LOGFILE!"
echo [INFO] Servidor iniciando em 0.0.0.0:8000>> "!LOGFILE!"
echo [INFO] URL PC: http://127.0.0.1:8000>> "!LOGFILE!"
echo [INFO] URL Celular: http://!IP!:8000>> "!LOGFILE!"

echo =============================================
echo Recipro Evolution em execução
echo PC:       http://127.0.0.1:8000
echo Celular:  http://!IP!:8000
echo =============================================
echo [INFO] Logs em: !LOGFILE!
echo.

echo [INFO] Uvicorn em execução... (CTRL+C para parar)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload >> "!LOGFILE!" 2>&1
if errorlevel 1 goto :fail

goto :eof

:fail
echo.
echo [ERRO] A execução falhou. Veja o log: !LOGFILE!
echo [ERRO] A execução falhou.>> "!LOGFILE!"
pause
exit /b 1
