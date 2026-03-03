@echo off
setlocal

cd /d "%~dp0"

echo [Recipro Evolution] Iniciando ambiente...
if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual em .venv...
    py -3.11 -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo =============================================
echo Recipro Evolution em execucao
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /R /C:"IPv4"') do (
    set IP=%%A
    goto :foundip
)
:foundip
set IP=%IP: =%
if "%IP%"=="" set IP=127.0.0.1

echo Acesse no PC: http://127.0.0.1:8000
echo Acesse no celular (mesmo Wi-Fi): http://%IP%:8000
echo =============================================
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

endlocal
