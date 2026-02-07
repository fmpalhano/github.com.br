#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def _load_points(path: str) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera um gráfico de Curva S (PNG) a partir de dados JSON."
    )
    parser.add_argument(
        "--data-json",
        required=True,
        help="Arquivo JSON com pontos da curva (ex.: [{\"label\":\"Jan\",\"planejado\":10,\"realizado\":8}]).",
    )
    parser.add_argument(
        "--output",
        default="curva_s.png",
        help="Arquivo PNG de saída (default: curva_s.png).",
    )
    parser.add_argument(
        "--title",
        default="Curva S da Obra",
        help="Título do gráfico.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    points = _load_points(args.data_json)

    labels = [p["label"] for p in points]
    planned = [p["planejado"] for p in points]
    actual = [p.get("realizado") for p in points]

    plt.figure(figsize=(10, 5))
    plt.plot(labels, planned, marker="o", label="Planejado")
    if any(value is not None for value in actual):
        plt.plot(labels, actual, marker="o", label="Realizado")

    plt.title(args.title)
    plt.xlabel("Período")
    plt.ylabel("% Acumulado")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output, dpi=150)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
