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

echo Executando exportador SIPROG...
python exportador.py --arquivo "%ARQUIVO_ENTRADA%" --data-inicio %DATA_INICIO% --data-fim %DATA_FIM% --status "%STATUS%" --colunas "%COLUNAS_EXTRAS%" --saida "%ARQUIVO_SAIDA%"

if errorlevel 1 (
  echo.
  echo [ERRO] Falha na exportacao. Verifique os parametros e dependencias.
  exit /b 1
)

echo.
echo [OK] Exportacao concluida: %ARQUIVO_SAIDA%
endlocal
