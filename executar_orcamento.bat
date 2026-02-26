@echo off
setlocal

cd /d "%~dp0"

rem Executa o app Tkinter sem abrir terminal (preferência pythonw/pyw)
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" /b pythonw -m src.orcamento_obra
    goto :eof
)

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" /b pyw -3 -m src.orcamento_obra
    goto :eof
)

rem Fallback (abre terminal apenas se pythonw/pyw não existir)
python -m src.orcamento_obra

endlocal
