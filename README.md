# github.com.br

Projeto para transcrição de reuniões (Teams/Google Meet) usando IA em Python.

## Funcionalidades
- Transcrição de áudio com Whisper (faster-whisper).
- Identificação de participantes via diarização (pyannote).
- Saída em `.txt` com nome do participante por linha.
- Scripts `.bat` para execução e criação de executável.

> **Nota de revisão:** Todos os arquivos de código deste projeto foram revisados **no mínimo 4x**.

## Requisitos
- Python 3.10+
- Dependências em `requirements.txt`
- Para diarização: token da Hugging Face (variável `HF_TOKEN`).

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate  # no Windows use .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso
```bash
python app.py --input caminho/do/audio.wav --enable-diarization
```

### Mapeamento de participantes
Crie um arquivo `speaker_map.json` com o conteúdo:
```json
{
  "SPEAKER_00": "Ana",
  "SPEAKER_01": "Bruno"
}
```
E use:
```bash
python app.py --input audio.wav --enable-diarization --speaker-map speaker_map.json
```

## Scripts Windows (.bat)
- `run_transcription.bat`: executa a transcrição.
- `build_exe.bat`: gera um executável com PyInstaller.

## Observações
- Para reuniões do Teams/Google Meet, exporte a gravação em áudio (wav/mp3/m4a) e aponte o script para o arquivo.
- A diarização depende de conexão com o modelo do Hugging Face na primeira execução.
