#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="docs/ui")


@app.get("/")
def index() -> object:
    return send_from_directory(app.static_folder, "index.html")


@app.get("/<path:filename>")
def static_files(filename: str) -> object:
    return send_from_directory(app.static_folder, filename)


@app.post("/api/generate")
def generate_report() -> object:
    payload = request.get_json(force=True, silent=True) or {}

    prompt = payload.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Informe a descrição da obra."}), 400

    model = payload.get("model", "gpt-4o-mini")
    output_md = payload.get("output_md", "relatorio.md")
    output_json = payload.get("output_json", "")
    convert_docx = bool(payload.get("convert_docx", True))
    log_file = payload.get("log_file", "relatorio.log")

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

    if output_json:
        command.extend(["--output-json", output_json])

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
