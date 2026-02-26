@echo off
setlocal

cd /d "%~dp0"

echo [1/3] Verificando PyInstaller...
where pyinstaller >nul 2>nul
if not %errorlevel%==0 (
    echo PyInstaller nao encontrado. Instalando...
    python -m pip install pyinstaller
)

echo [2/3] Limpando build anterior...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist OrcamentoObraEletrica.spec del /q OrcamentoObraEletrica.spec

echo [3/3] Gerando EXE standalone...
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name OrcamentoObraEletrica ^
  --hidden-import src.base_materiais ^
  --hidden-import src.material_storage ^
  src\orcamento_obra.py

if not %errorlevel%==0 (
    echo.
    echo FALHA ao gerar EXE.
    exit /b 1
)

echo.
echo EXE gerado com sucesso em: dist\OrcamentoObraEletrica.exe
endlocal
