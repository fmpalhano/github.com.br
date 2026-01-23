@echo off
REM Revisado 4x
REM Uso: run_transcription.bat "caminho\para\audio.wav"

set INPUT=%~1
if "%INPUT%"=="" (
  echo Informe o caminho do audio.
  exit /b 1
)

python app.py --input "%INPUT%" --enable-diarization
