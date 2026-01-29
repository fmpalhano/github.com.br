#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import json

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="docs/ui")
UPLOADS_DIR = Path("uploads")


@app.get("/")
def index() -> object:
    return send_from_directory(app.static_folder, "index.html")


@app.get("/<path:filename>")
def static_files(filename: str) -> object:
    return send_from_directory(app.static_folder, filename)


@app.post("/api/generate")
def generate_report() -> object:
    payload = request.form

    prompt = payload.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Informe a descrição da obra."}), 400

    model = payload.get("model", "llama3.1")
    ollama_url = payload.get("ollama_url", "http://localhost:11434")
    output_md = payload.get("output_md", "relatorio.md")
    output_json = payload.get("output_json", "")
    convert_docx = payload.get("convert_docx", "true").lower() == "true"
    offline = payload.get("offline", "false").lower() == "true"
    log_file = payload.get("log_file", "relatorio.log")
    ollama_timeout = payload.get("ollama_timeout", "180")

    uploads = {"imagens_relatorio": [], "imagens_kpi": [], "dwg_arquivo": ""}
    UPLOADS_DIR.mkdir(exist_ok=True)

    for field in ("imagens_relatorio", "imagens_kpi"):
        for file_storage in request.files.getlist(field):
            if not file_storage.filename:
                continue
            filename = secure_filename(file_storage.filename)
            target = UPLOADS_DIR / filename
            file_storage.save(target)
            uploads[field].append({"caminho": str(target), "legenda": filename})

    dwg_file = request.files.get("dwg_arquivo")
    if dwg_file and dwg_file.filename:
        filename = secure_filename(dwg_file.filename)
        target = UPLOADS_DIR / filename
        dwg_file.save(target)
        uploads["dwg_arquivo"] = str(target)

    override_path = Path("override.json")
    override_path.write_text(
        json.dumps(uploads, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    command = [
        sys.executable,
        str(Path(__file__).with_name("generate_report.py")),
        "--prompt",
        prompt,
        "--model",
        model,
        "--output-md",
        output_md,
    ]
    command.extend(["--ollama-url", ollama_url])
    command.extend(["--ollama-timeout", ollama_timeout])

    if output_json:
        command.extend(["--output-json", output_json])

    command.extend(["--override-json", str(override_path)])

    if offline:
        command.append("--offline")

    if convert_docx:
        command.append("--convert-docx")

    if log_file:
        command.extend(["--log-file", log_file])

    result = subprocess.run(command, capture_output=True, text=True)

    response = {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

    status = 200 if result.returncode == 0 else 500
    return jsonify(response), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
