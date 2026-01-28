@echo off
setlocal

set "PORT=8000"
set "UI_DIR=%~dp0docs\ui"

if not exist "%UI_DIR%\index.html" (
  echo Interface nao encontrada em %UI_DIR%.
  echo Verifique se o repositorio esta completo.
  exit /b 1
)

echo Iniciando servidor em http://localhost:%PORT%
python -m http.server %PORT% --directory "%UI_DIR%"
