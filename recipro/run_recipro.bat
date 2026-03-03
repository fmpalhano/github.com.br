@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

if not exist "logs" mkdir logs
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set LOGFILE=logs\run_!TS!.log

echo [Recipro Evolution] Iniciando... > "!LOGFILE!"
echo Diretorio: %CD%>> "!LOGFILE!"
echo Timestamp: !TS!>> "!LOGFILE!"

echo.
echo [INFO] Log desta execucao: !LOGFILE!
echo [INFO] Se algo falhar, envie este arquivo.
echo.

set PY_CMD=

where py >nul 2>nul
if %errorlevel%==0 (
    echo [INFO] py launcher encontrado.>> "!LOGFILE!"
    py -0p >> "!LOGFILE!" 2>&1

    py -3.11 -c "import sys" >nul 2>nul
    if !errorlevel! == 0 (
        set PY_CMD=py -3.11
    )

    if not defined PY_CMD (
        py -3.10 -c "import sys" >nul 2>nul
        if !errorlevel! == 0 (
            set PY_CMD=py -3.10
        )
    )

    if not defined PY_CMD (
        py -3 -c "import sys" >nul 2>nul
        if !errorlevel! == 0 (
            set PY_CMD=py -3
        )
    )
)

if not defined PY_CMD (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PY_CMD=python
    )
)

if not defined PY_CMD (
    echo [ERRO] Python nao encontrado no PATH.
    echo [ERRO] Instale Python 3.11 ou 3.10 e marque "Add python.exe to PATH".
    echo [ERRO] Python nao encontrado no PATH.>> "!LOGFILE!"
    pause
    exit /b 1
)

echo [INFO] Python selecionado: !PY_CMD!
echo [INFO] Python selecionado: !PY_CMD!>> "!LOGFILE!"
!PY_CMD! -c "import sys; print('[INFO] Versao Python:', sys.version)" >> "!LOGFILE!" 2>&1

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
echo Recipro Evolution em execucao
echo PC:       http://127.0.0.1:8000
echo Celular:  http://!IP!:8000
echo =============================================
echo [INFO] Logs em: !LOGFILE!
echo.

echo [INFO] Uvicorn em execucao... (CTRL+C para parar)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload >> "!LOGFILE!" 2>&1
if errorlevel 1 goto :fail

goto :eof

:fail
echo.
echo [ERRO] A execucao falhou. Veja o log: !LOGFILE!
echo [ERRO] A execucao falhou.>> "!LOGFILE!"
pause
exit /b 1
