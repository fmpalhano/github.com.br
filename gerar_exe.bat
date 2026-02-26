@echo off
setlocal

cd /d "%~dp0"

where pyinstaller >nul 2>nul
if not %errorlevel%==0 (
    echo Instalando PyInstaller...
    python -m pip install pyinstaller
)

pyinstaller --noconfirm --clean --onefile --windowed --name OrcamentoObraEletrica -m src.orcamento_obra

echo.
echo EXE gerado em: dist\OrcamentoObraEletrica.exe

endlocal
