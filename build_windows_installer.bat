@echo off
setlocal

set "APP_NAME=GrupoSetupRelatorios"
set "APP_FILE=app_server.py"

where pyinstaller >nul 2>&1
if errorlevel 1 (
  echo PyInstaller nao encontrado. Instalando...
  python -m pip install --upgrade pyinstaller
)

if not exist "%APP_FILE%" (
  echo Arquivo %APP_FILE% nao encontrado.
  exit /b 1
)

echo Gerando executavel...
pyinstaller --noconfirm --onefile --name "%APP_NAME%" --add-data "docs\ui;docs\ui" "%APP_FILE%"

echo.
 echo Executavel gerado em dist\%APP_NAME%.exe
 echo Para executar, basta abrir o arquivo acima.
