@echo off
setlocal

REM ===== Configuracao padrao para teste do exportador SIPROG =====
set "ARQUIVO_ENTRADA=modeloProgramacao.xlsx"
set "ARQUIVO_SAIDA=exportacao_siprog_teste.xlsx"
set "DATA_INICIO=2026-02-01"
set "DATA_FIM=2026-02-20"
set "STATUS=LIB/LOG"

REM Colunas extras opcionais (alem do layout obrigatorio).
REM Deixe vazio para exportar somente as colunas obrigatorias.
set "COLUNAS_EXTRAS="

REM Mantenha 1 para nao fechar a janela automaticamente ao final.
set "PAUSAR_NO_FINAL=1"
set "MODO_TELA=1"
set "ESCOLHER_ABA=1"

echo =============================================
echo   Exportador SIPROG - Execucao de teste
echo =============================================

echo [1/3] Validando Python...
where python >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Python nao encontrado no PATH.
  echo        Instale o Python e marque a opcao "Add Python to PATH".
  goto :falha
)

echo [2/3] Executando exportador...
if "%MODO_TELA%"=="1" (
  echo      Modo tela habilitado: selecione a planilha e a pasta de trabalho.
  if "%ESCOLHER_ABA%"=="1" (
    python exportador.py --selecionar-arquivos --selecionar-aba --data-inicio %DATA_INICIO% --data-fim %DATA_FIM% --status "%STATUS%" --colunas "%COLUNAS_EXTRAS%" --saida "%ARQUIVO_SAIDA%"
  ) else (
    python exportador.py --selecionar-arquivos --data-inicio %DATA_INICIO% --data-fim %DATA_FIM% --status "%STATUS%" --colunas "%COLUNAS_EXTRAS%" --saida "%ARQUIVO_SAIDA%"
  )
) else (
  if "%ESCOLHER_ABA%"=="1" (
    python exportador.py --arquivo "%ARQUIVO_ENTRADA%" --selecionar-aba --data-inicio %DATA_INICIO% --data-fim %DATA_FIM% --status "%STATUS%" --colunas "%COLUNAS_EXTRAS%" --saida "%ARQUIVO_SAIDA%"
  ) else (
    python exportador.py --arquivo "%ARQUIVO_ENTRADA%" --data-inicio %DATA_INICIO% --data-fim %DATA_FIM% --status "%STATUS%" --colunas "%COLUNAS_EXTRAS%" --saida "%ARQUIVO_SAIDA%"
  )
)

if errorlevel 1 (
  echo [ERRO] Falha na exportacao. Revise parametros, colunas obrigatorias e dependencias.
  goto :falha
)

echo [3/3] Concluido com sucesso.
echo [OK] Arquivo gerado: %ARQUIVO_SAIDA%
goto :fim

:falha
echo.
echo A execucao terminou com erro.

:fim
if "%PAUSAR_NO_FINAL%"=="1" (
  echo.
  pause
)

endlocal
