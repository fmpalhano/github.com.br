#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import openai
import pystache


def _strip_code_fences(text: str) -> str:
    fenced = re.search(r"```(?:json)?\n(.*?)```", text, re.DOTALL)
    if fenced:
        return fenced.group(1).strip()
    return text.strip()


def _extract_json(text: str) -> dict:
    cleaned = _strip_code_fences(text)
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return json.loads(cleaned)
    brace_start = cleaned.find("{")
    brace_end = cleaned.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        return json.loads(cleaned[brace_start : brace_end + 1])
    raise ValueError("Resposta da IA não contém JSON válido.")


def _load_prompt(args: argparse.Namespace) -> str:
    if args.prompt:
        return args.prompt
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise ValueError("Informe --prompt, --prompt-file ou envie texto via stdin.")


def _load_data_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _call_openai(prompt: str, model: str) -> dict:
    client = openai.OpenAI()
    system_prompt = (
        "Você é um assistente que extrai dados para preencher um template de relatório de obra. "
        "Responda APENAS com um JSON válido. Use exatamente estas chaves: "
        "titulo_obra, cliente, localidade, data_relatorio, imagem_capa, descricao_obra, "
        "extensao_mt_km, extensao_bt_km, total_postes, pep_partes (lista), "
        "consideracoes_ressalvas, materiais, data_inicio, data_previsao_conclusao, "
        "equipamentos (lista), dificuldades (lista), curva_s, observacoes_finais, "
        "registros_fotograficos (lista). "
        "Cada item de pep_partes deve ter: parte_nome, obra, pep, poste, status. "
        "Cada item de registros_fotograficos deve ter: secao e itens (lista). "
        "Cada item em itens deve ter: foto e descricao. "
        "Se algum dado não existir, use string vazia ou listas vazias."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content
    return _extract_json(content)


def _render_template(template_path: Path, data: dict) -> str:
    template = template_path.read_text(encoding="utf-8")
    renderer = pystache.Renderer(escape=lambda u: u)
    return renderer.render(template, data)


def _write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _convert_to_docx(markdown_path: Path, docx_path: Path) -> None:
    if not shutil.which("pandoc"):
        raise RuntimeError("pandoc não encontrado no PATH.")
    subprocess.run(
        ["pandoc", str(markdown_path), "-o", str(docx_path)],
        check=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera relatório de obra em Markdown e opcionalmente DOCX usando IA."
    )
    parser.add_argument(
        "--template",
        default="docs/template-obra.md",
        help="Caminho do template Markdown.",
    )
    parser.add_argument("--prompt", help="Texto com a descrição da obra.")
    parser.add_argument("--prompt-file", help="Arquivo contendo a descrição da obra.")
    parser.add_argument(
        "--data-json",
        help="JSON pronto com os dados (pula a chamada à IA).",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        help="Modelo OpenAI (default: gpt-4o-mini).",
    )
    parser.add_argument(
        "--output-md",
        default="relatorio.md",
        help="Arquivo Markdown de saída.",
    )
    parser.add_argument(
        "--output-docx",
        default="relatorio.docx",
        help="Arquivo DOCX de saída.",
    )
    parser.add_argument(
        "--convert-docx",
        action="store_true",
        help="Converte o Markdown gerado em DOCX usando pandoc.",
    )
    parser.add_argument(
        "--output-json",
        help="Salva o JSON gerado pela IA.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.data_json:
        data = _load_data_json(args.data_json)
    else:
        prompt = _load_prompt(args)
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("Defina a variável OPENAI_API_KEY.")
        data = _call_openai(prompt, args.model)

    template_path = Path(args.template)
    output_md = Path(args.output_md)
    output_docx = Path(args.output_docx)

    rendered = _render_template(template_path, data)
    _write_output(output_md, rendered)

    if args.output_json:
        _write_output(Path(args.output_json), json.dumps(data, ensure_ascii=False, indent=2))

    if args.convert_docx:
        _convert_to_docx(output_md, output_docx)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
