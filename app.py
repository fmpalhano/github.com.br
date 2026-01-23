"""Reunião Transcriber - Revisado 4x.

Transcreve áudio de reuniões com identificação de participantes (speaker diarization).
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from faster_whisper import WhisperModel
from pyannote.audio import Pipeline


@dataclass
class Segment:
    start: float
    end: float
    text: str
    speaker: Optional[str] = None


@dataclass
class DiarizationSegment:
    start: float
    end: float
    speaker: str


def load_speaker_map(path: Optional[Path]) -> Dict[str, str]:
    if not path:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def transcribe_audio(
    audio_path: Path,
    model_size: str,
    device: str,
    compute_type: str,
    language: Optional[str],
) -> List[Segment]:
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True,
    )
    results: List[Segment] = []
    for segment in segments:
        results.append(Segment(start=segment.start, end=segment.end, text=segment.text))
    return results


def diarize_audio(audio_path: Path, hf_token: str) -> List[DiarizationSegment]:
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token,
    )
    diarization = pipeline(str(audio_path))
    results: List[DiarizationSegment] = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        results.append(DiarizationSegment(start=turn.start, end=turn.end, speaker=speaker))
    return results


def overlap_duration(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    return max(0.0, min(a_end, b_end) - max(a_start, b_start))


def assign_speakers(
    segments: List[Segment],
    diarization: List[DiarizationSegment],
    speaker_map: Dict[str, str],
) -> List[Segment]:
    for segment in segments:
        best_speaker = None
        best_overlap = 0.0
        for diar in diarization:
            overlap = overlap_duration(segment.start, segment.end, diar.start, diar.end)
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = diar.speaker
        if best_speaker:
            segment.speaker = speaker_map.get(best_speaker, best_speaker)
        else:
            segment.speaker = "Speaker"
    return segments


def format_output(segments: Iterable[Segment]) -> str:
    lines: List[str] = []
    for segment in segments:
        speaker = segment.speaker or "Speaker"
        lines.append(f"{speaker}: {segment.text.strip()}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcreve áudio de reuniões (Teams/Meet) com identificação de participantes.",
    )
    parser.add_argument("--input", required=True, help="Caminho do áudio (wav/mp3/m4a).")
    parser.add_argument(
        "--output",
        help="Caminho do arquivo .txt de saída. Default: mesmo nome do áudio.",
    )
    parser.add_argument("--model", default="medium", help="Modelo Whisper (ex: tiny, base, small, medium, large-v3).")
    parser.add_argument("--device", default="cpu", help="Dispositivo: cpu, cuda.")
    parser.add_argument("--compute-type", default="int8", help="Tipo de precisão (int8, float16, float32).")
    parser.add_argument("--language", default=None, help="Idioma (ex: pt, en). Default: auto.")
    parser.add_argument(
        "--enable-diarization",
        action="store_true",
        help="Ativa diarização por speaker (requer token Hugging Face).",
    )
    parser.add_argument(
        "--speaker-map",
        help="JSON com mapa de speaker (ex: {'SPEAKER_00': 'Ana'}).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audio_path = Path(args.input)
    if not audio_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")

    output_path = Path(args.output) if args.output else audio_path.with_suffix(".txt")
    speaker_map = load_speaker_map(Path(args.speaker_map)) if args.speaker_map else {}

    segments = transcribe_audio(
        audio_path=audio_path,
        model_size=args.model,
        device=args.device,
        compute_type=args.compute_type,
        language=args.language,
    )

    if args.enable_diarization:
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            raise EnvironmentError("Defina a variável de ambiente HF_TOKEN para diarização.")
        diarization = diarize_audio(audio_path, hf_token)
        segments = assign_speakers(segments, diarization, speaker_map)
    else:
        for segment in segments:
            segment.speaker = "Speaker"

    output_text = format_output(segments)
    output_path.write_text(output_text, encoding="utf-8")
    print(f"Transcrição salva em: {output_path}")


if __name__ == "__main__":
    main()
