@echo off
setlocal

cd /d "%~dp0"

rem Executa o app Tkinter sem abrir terminal (preferência pythonw/pyw)
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" /b pythonw src\orcamento_obra.py
    goto :eof
)

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" /b pyw -3 src\orcamento_obra.py
    goto :eof
)

rem Fallback (abre terminal apenas se pythonw/pyw não existir)
python src\orcamento_obra.py

endlocal
