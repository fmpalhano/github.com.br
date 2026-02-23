@echo off
setlocal

REM ===== Configuracao padrao para teste do exportador SIPROG =====
set "ARQUIVO_ENTRADA=modeloProgramacao.xlsx"
set "ARQUIVO_SAIDA=exportacao_siprog_teste.xlsx"
set "DATA_INICIO=2026-02-01"
set "DATA_FIM=2026-02-20"
set "STATUS=LIB/LOG"
set "PRAZO_CONCLUSAO="
set "DATA_PROGRAMACAO="

REM Controles de execucao:
set "PAUSAR_NO_FINAL=1"
set "MODO_TELA=1"
set "GUI_EXECUCAO=1"
set "SELECIONAR_DATAS=1"

echo =============================================
echo   Exportador SIPROG - Execucao de teste
echo =============================================

echo [1/3] Validando Python...
where python >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Python nao encontrado no PATH.
  goto :falha
)

echo [2/3] Executando exportador...
set "EXTRA_FLAGS="
if "%GUI_EXECUCAO%"=="1" set "EXTRA_FLAGS=%EXTRA_FLAGS% --gui-execucao"
if "%SELECIONAR_DATAS%"=="1" set "EXTRA_FLAGS=%EXTRA_FLAGS% --selecionar-datas"

if "%MODO_TELA%"=="1" (
  python exportador.py --selecionar-arquivos %EXTRA_FLAGS% --data-inicio %DATA_INICIO% --data-fim %DATA_FIM% --status "%STATUS%" --prazo-conclusao "%PRAZO_CONCLUSAO%" --data-programacao "%DATA_PROGRAMACAO%" --saida "%ARQUIVO_SAIDA%"
) else (
  python exportador.py --arquivo "%ARQUIVO_ENTRADA%" %EXTRA_FLAGS% --data-inicio %DATA_INICIO% --data-fim %DATA_FIM% --status "%STATUS%" --prazo-conclusao "%PRAZO_CONCLUSAO%" --data-programacao "%DATA_PROGRAMACAO%" --saida "%ARQUIVO_SAIDA%"
)

if errorlevel 1 (
  echo [ERRO] Falha na exportacao. Revise parametros e dependencias.
  goto :falha
)

echo [3/3] Concluido com sucesso.
goto :fim

:falha
echo.
echo A execucao terminou com erro.

:fim
if "%PAUSAR_NO_FINAL%"=="1" pause
endlocal
