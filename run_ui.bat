@echo off
setlocal

set "PORT=8000"
set "APP_FILE=%~dp0app_server.py"

if not exist "%APP_FILE%" (
  echo Arquivo %APP_FILE% nao encontrado.
  echo Verifique se o repositorio esta completo.
  exit /b 1
)

echo Iniciando servidor em http://localhost:%PORT%
python "%APP_FILE%"
