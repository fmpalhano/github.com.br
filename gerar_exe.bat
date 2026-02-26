@echo off
setlocal

cd /d "%~dp0"

echo [1/4] Verificando Python...
python --version >nul 2>nul
if not %errorlevel%==0 (
    echo Python nao encontrado no PATH.
    exit /b 1
)

echo [2/4] Verificando modulo PyInstaller...
python -m PyInstaller --version >nul 2>nul
if not %errorlevel%==0 (
    echo PyInstaller nao encontrado neste Python. Instalando...
    python -m pip install --user pyinstaller
    if not %errorlevel%==0 (
        echo Falha ao instalar PyInstaller.
        exit /b 1
    )
)

echo [3/4] Limpando build anterior...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist OrcamentoObraEletrica.spec del /q OrcamentoObraEletrica.spec

echo [4/4] Gerando EXE standalone...
python -m PyInstaller ^
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
