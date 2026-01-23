@echo off
REM Revisado 4x
REM Gera executavel usando PyInstaller

pip install pyinstaller
pyinstaller --onefile --name transcritor_reuniao app.py
