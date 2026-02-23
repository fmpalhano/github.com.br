@echo off
setlocal

REM ==================================================
REM Build .exe do exportador SIPROG
REM Assinado por: Felipe de Moraes Palhano
REM ==================================================

echo =============================================
echo   Build EXE - Exportador SIPROG
echo   Assinado por: Felipe de Moraes Palhano
echo =============================================

echo [1/4] Validando Python...
where python >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Python nao encontrado no PATH.
  goto :falha
)

echo [2/4] Instalando/atualizando PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
  echo [ERRO] Falha ao instalar PyInstaller.
  goto :falha
)

echo [3/4] Gerando executavel...
python -m PyInstaller --onefile --name exportador_siprog exportador.py
if errorlevel 1 (
  echo [ERRO] Falha ao gerar o executavel.
  goto :falha
)

echo [4/4] Concluido.
echo [OK] Executavel gerado em: dist\exportador_siprog.exe
goto :fim

:falha
echo.
echo A geracao do .exe terminou com erro.

:fim
echo.
pause
endlocal
