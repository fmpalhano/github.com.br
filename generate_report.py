#!/usr/bin/env python3
import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib import request as urlrequest

import openai
import pystache


class LogCounter(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.counts = {"debug": 0, "info": 0, "warning": 0, "error": 0, "critical": 0}

    def emit(self, record: logging.LogRecord) -> None:
        level = record.levelname.lower()
        if level in self.counts:
            self.counts[level] += 1


def _configure_logging(log_level: str, log_file: str | None) -> LogCounter:
    handlers: list[logging.Handler] = []
    handler = LogCounter()
    handlers.append(handler)

    console = logging.StreamHandler()
    console.setLevel(log_level)
    handlers.append(console)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )
    return handler


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
    logging.error("Resposta da IA não contém JSON válido.")
    raise ValueError("Resposta da IA não contém JSON válido.")


def _load_prompt(args: argparse.Namespace) -> str:
    if args.prompt:
        return args.prompt
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    logging.error("Nenhum prompt fornecido.")
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
        "registros_fotograficos (lista), kpi_resumo, kpi_indicadores (lista), "
        "imagens_relatorio (lista), imagens_kpi (lista), dwg_arquivo. "
        "Cada item de pep_partes deve ter: parte_nome, obra, pep, poste, status. "
        "Cada item de registros_fotograficos deve ter: secao e itens (lista). "
        "Cada item em itens deve ter: foto e descricao. "
        "Cada item de kpi_indicadores deve ter: nome, valor, unidade. "
        "Cada item de imagens_relatorio e imagens_kpi deve ter: caminho e legenda. "
        "Se algum dado não existir, use string vazia ou listas vazias."
    )
    logging.info("Chamando OpenAI com modelo %s.", model)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    except openai.AuthenticationError as exc:
        logging.error("Falha de autenticação com a OpenAI.")
        raise RuntimeError(
            "Chave OpenAI inválida ou ausente. "
            "Verifique a variável OPENAI_API_KEY e gere uma nova chave, se necessário."
        ) from exc
    content = response.choices[0].message.content
    logging.debug("Resposta bruta da IA recebida.")
    return _extract_json(content)


def _call_ollama(prompt: str, model: str, base_url: str) -> dict:
    system_prompt = (
        "Você é um assistente que extrai dados para preencher um template de relatório de obra. "
        "Responda APENAS com um JSON válido. Use exatamente estas chaves: "
        "titulo_obra, cliente, localidade, data_relatorio, imagem_capa, descricao_obra, "
        "extensao_mt_km, extensao_bt_km, total_postes, pep_partes (lista), "
        "consideracoes_ressalvas, materiais, data_inicio, data_previsao_conclusao, "
        "equipamentos (lista), dificuldades (lista), curva_s, observacoes_finais, "
        "registros_fotograficos (lista), kpi_resumo, kpi_indicadores (lista), "
        "imagens_relatorio (lista), imagens_kpi (lista), dwg_arquivo. "
        "Cada item de pep_partes deve ter: parte_nome, obra, pep, poste, status. "
        "Cada item de registros_fotograficos deve ter: secao e itens (lista). "
        "Cada item em itens deve ter: foto e descricao. "
        "Cada item de kpi_indicadores deve ter: nome, valor, unidade. "
        "Cada item de imagens_relatorio e imagens_kpi deve ter: caminho e legenda. "
        "Se algum dado não existir, use string vazia ou listas vazias."
    )
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
    ).encode("utf-8")
    endpoint = base_url.rstrip("/") + "/api/chat"
    logging.info("Chamando Ollama em %s com modelo %s.", endpoint, model)
    req = urlrequest.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlrequest.urlopen(req, timeout=60) as response:
            body = response.read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        logging.error("Falha ao chamar Ollama.")
        raise RuntimeError(
            "Não foi possível acessar o Ollama. Verifique se o serviço está ativo "
            "em http://localhost:11434 e se o modelo está instalado."
        ) from exc

    data = json.loads(body)
    content = data.get("message", {}).get("content", "")
    if not content:
        raise RuntimeError("Resposta vazia do Ollama.")
    return _extract_json(content)


def _render_template(template_path: Path, data: dict) -> str:
    template = template_path.read_text(encoding="utf-8")
    renderer = pystache.Renderer(escape=lambda u: u)
    return renderer.render(template, data)


def _write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _convert_to_docx(markdown_path: Path, docx_path: Path) -> bool:
    if not shutil.which("pandoc"):
        logging.warning("pandoc não encontrado no PATH. Ignorando conversão para DOCX.")
        return False
    subprocess.run(
        ["pandoc", str(markdown_path), "-o", str(docx_path)],
        check=True,
    )
    return True


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
        "--offline",
        action="store_true",
        help="Gera relatório sem chamada à IA (modo offline).",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        help="Modelo OpenAI (default: gpt-4o-mini).",
    )
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "ollama"],
        help="Provedor de IA (openai ou ollama).",
    )
    parser.add_argument(
        "--ollama-url",
        default=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        help="URL base do Ollama (default: http://localhost:11434).",
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
    parser.add_argument(
        "--override-json",
        help="JSON com campos que sobrescrevem o resultado da IA.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Nível de log (default: INFO).",
    )
    parser.add_argument(
        "--log-file",
        help="Salva logs em arquivo para auditoria.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    log_counter = _configure_logging(args.log_level, args.log_file)

    try:
        if args.data_json:
            data = _load_data_json(args.data_json)
            logging.info("Dados carregados do JSON %s.", args.data_json)
        else:
            prompt = _load_prompt(args)
            if args.offline:
                data = {
                    "titulo_obra": "Relatório de Obra",
                    "cliente": "",
                    "localidade": "",
                    "data_relatorio": date.today().isoformat(),
                    "imagem_capa": "",
                    "descricao_obra": prompt,
                    "extensao_mt_km": "",
                    "extensao_bt_km": "",
                    "total_postes": "",
                    "pep_partes": [],
                    "consideracoes_ressalvas": "",
                    "materiais": "",
                    "data_inicio": "",
                    "data_previsao_conclusao": "",
                    "equipamentos": [],
                    "dificuldades": [],
                    "curva_s": "",
                    "observacoes_finais": "",
                    "registros_fotograficos": [],
                    "kpi_resumo": "",
                    "kpi_indicadores": [],
                    "imagens_relatorio": [],
                    "imagens_kpi": [],
                    "dwg_arquivo": "",
                }
                logging.info("Modo offline ativo. Relatório gerado sem IA.")
            else:
                if args.provider == "ollama":
                    data = _call_ollama(prompt, args.model, args.ollama_url)
                else:
                    if not os.getenv("OPENAI_API_KEY"):
                        logging.error("OPENAI_API_KEY não definida.")
                        raise RuntimeError("Defina a variável OPENAI_API_KEY.")
                    data = _call_openai(prompt, args.model)

        if args.override_json:
            override_data = _load_data_json(args.override_json)
            data.update(override_data)
            logging.info("Campos sobrescritos via %s.", args.override_json)

        template_path = Path(args.template)
        output_md = Path(args.output_md)
        output_docx = Path(args.output_docx)

        rendered = _render_template(template_path, data)
        _write_output(output_md, rendered)
        logging.info("Markdown gerado em %s.", output_md)

        if args.output_json:
            _write_output(
                Path(args.output_json),
                json.dumps(data, ensure_ascii=False, indent=2),
            )
            logging.info("JSON salvo em %s.", args.output_json)

        if args.convert_docx:
            converted = _convert_to_docx(output_md, output_docx)
            if converted:
                logging.info("DOCX gerado em %s.", output_docx)
    finally:
        logging.info(
            "Resumo de logs: debug=%d info=%d warning=%d error=%d critical=%d",
            log_counter.counts["debug"],
            log_counter.counts["info"],
            log_counter.counts["warning"],
            log_counter.counts["error"],
            log_counter.counts["critical"],
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
