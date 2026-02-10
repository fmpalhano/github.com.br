@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 goetic_system.py
    goto :eof
)

where python >nul 2>nul
if %errorlevel%==0 (
    python goetic_system.py
    goto :eof
)

echo Python nao encontrado no PATH.
echo Instale o Python 3 e tente novamente.
pause
