#!/usr/bin/env python3
"""Exportador de planilhas para ingestão no SIPROG."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

DEFAULT_OUTPUT = "exportacao_siprog.xlsx"


class ExportadorErro(ValueError):
    """Erro de validação para entradas do exportador."""


def carregar_base(caminho: str, sheet_name: str | int | None = None) -> pd.DataFrame:
    """Carrega um arquivo Excel e retorna o DataFrame da aba selecionada."""
    arquivo = Path(caminho)
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")

    return pd.read_excel(arquivo, sheet_name=sheet_name)


def aplicar_filtros(
    df: pd.DataFrame,
    data_coluna: str,
    data_inicio: str | None,
    data_fim: str | None,
    status_coluna: str,
    status: str | None,
) -> pd.DataFrame:
    """Aplica filtros de data e status quando as colunas existem."""
    resultado = df.copy()

    if data_coluna in resultado.columns:
        resultado[data_coluna] = pd.to_datetime(resultado[data_coluna], errors="coerce")

        if data_inicio:
            inicio = pd.to_datetime(data_inicio)
            resultado = resultado[resultado[data_coluna] >= inicio]

        if data_fim:
            fim = pd.to_datetime(data_fim)
            resultado = resultado[resultado[data_coluna] <= fim]

    if status and status_coluna in resultado.columns:
        resultado = resultado[resultado[status_coluna].astype(str).str.upper() == status.upper()]

    return resultado


def _normalizar_colunas(colunas: str | None) -> list[str]:
    if not colunas:
        return []
    return [col.strip() for col in colunas.split(",") if col.strip()]


def validar_colunas_solicitadas(df: pd.DataFrame, colunas: Iterable[str]) -> None:
    faltantes = [col for col in colunas if col not in df.columns]
    if faltantes:
        raise ExportadorErro(
            "As seguintes colunas não existem na base: " + ", ".join(faltantes)
        )


def selecionar_colunas(df: pd.DataFrame, colunas: str | None) -> pd.DataFrame:
    colunas_lista = _normalizar_colunas(colunas)
    if not colunas_lista:
        return df

    validar_colunas_solicitadas(df, colunas_lista)
    return df[colunas_lista]


def exportar(df: pd.DataFrame, saida: str) -> None:
    destino = Path(saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(destino, index=False)

    print(f"Arquivo gerado: {destino}")
    print(f"Total de registros exportados: {len(df)}")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Exportador SIPROG")

    parser.add_argument("--arquivo", required=True, help="Caminho do arquivo .xlsx de entrada")
    parser.add_argument("--aba", help="Nome (ou índice) da aba a ser exportada")

    parser.add_argument("--data-coluna", default="Data", help="Nome da coluna de data")
    parser.add_argument("--data-inicio", help="Data inicial no formato YYYY-MM-DD")
    parser.add_argument("--data-fim", help="Data final no formato YYYY-MM-DD")

    parser.add_argument("--status-coluna", default="Status", help="Nome da coluna de status")
    parser.add_argument("--status", help="Valor do status para filtro")

    parser.add_argument(
        "--colunas",
        help="Colunas separadas por vírgula para exportação (ex: equipe,tecnico,data)",
    )
    parser.add_argument("--saida", default=DEFAULT_OUTPUT, help="Arquivo de saída .xlsx")

    return parser


def _parse_sheet_name(sheet_name: str | None) -> str | int | None:
    if sheet_name is None:
        return None
    return int(sheet_name) if sheet_name.isdigit() else sheet_name


def main() -> None:
    parser = construir_parser()
    args = parser.parse_args()

    df = carregar_base(args.arquivo, sheet_name=_parse_sheet_name(args.aba))
    df = aplicar_filtros(
        df,
        data_coluna=args.data_coluna,
        data_inicio=args.data_inicio,
        data_fim=args.data_fim,
        status_coluna=args.status_coluna,
        status=args.status,
    )
    df = selecionar_colunas(df, args.colunas)

    exportar(df, args.saida)


if __name__ == "__main__":
    main()
