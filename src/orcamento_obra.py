from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CATALOGO_COLUNAS_OBRIGATORIAS = {
    "ATIVACAO",
    "LINHA_VIVA",
    "TIPOESTR",
    "CODLISTA",
    "RESUMO",
    "PRIORIDADE",
}


@dataclass(frozen=True)
class MaterialCatalogo:
    ativacao: str
    linha_viva: str
    tipo_estr: str
    cod_lista: str
    resumo: str
    prioridade: int | None


@dataclass(frozen=True)
class ItemOrcamento:
    cod_lista: str
    quantidade: float
    preco_unitario: float

    @property
    def subtotal(self) -> float:
        return self.quantidade * self.preco_unitario


@dataclass(frozen=True)
class OrcamentoMateriais:
    itens: list[ItemOrcamento]
    taxa_imprevistos_percentual: float = 5.0

    @property
    def subtotal(self) -> float:
        return sum(item.subtotal for item in self.itens)

    @property
    def valor_imprevistos(self) -> float:
        return self.subtotal * (self.taxa_imprevistos_percentual / 100)

    @property
    def total_geral(self) -> float:
        return self.subtotal + self.valor_imprevistos


def _validar_colunas(obtidas: set[str], obrigatorias: set[str], arquivo: Path) -> None:
    faltando = obrigatorias - obtidas
    if faltando:
        raise ValueError(
            f"Arquivo inválido ({arquivo}). Colunas faltando: {', '.join(sorted(faltando))}"
        )


def _normalizar_texto(valor: str | None) -> str:
    return (valor or "").strip()


def carregar_catalogo_materiais(caminho_csv: Path) -> dict[str, MaterialCatalogo]:
    with caminho_csv.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        _validar_colunas(set(leitor.fieldnames or []), CATALOGO_COLUNAS_OBRIGATORIAS, caminho_csv)

        catalogo: dict[str, MaterialCatalogo] = {}
        for linha in leitor:
            codigo = _normalizar_texto(linha["CODLISTA"])
            if not codigo:
                continue
            prioridade_raw = _normalizar_texto(linha["PRIORIDADE"])
            prioridade = int(prioridade_raw) if prioridade_raw.isdigit() else None

            catalogo[codigo] = MaterialCatalogo(
                ativacao=_normalizar_texto(linha["ATIVACAO"]),
                linha_viva=_normalizar_texto(linha["LINHA_VIVA"]),
                tipo_estr=_normalizar_texto(linha["TIPOESTR"]),
                cod_lista=codigo,
                resumo=_normalizar_texto(linha["RESUMO"]),
                prioridade=prioridade,
            )
    return catalogo


def carregar_itens_orcamento(caminho_csv: Path) -> list[ItemOrcamento]:
    colunas = {"CODLISTA", "QUANTIDADE", "PRECO_UNITARIO"}
    with caminho_csv.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        _validar_colunas(set(leitor.fieldnames or []), colunas, caminho_csv)

        itens: list[ItemOrcamento] = []
        for linha in leitor:
            itens.append(
                ItemOrcamento(
                    cod_lista=_normalizar_texto(linha["CODLISTA"]),
                    quantidade=float(linha["QUANTIDADE"]),
                    preco_unitario=float(linha["PRECO_UNITARIO"]),
                )
            )
    return itens


def formatar_moeda(valor: float) -> str:
    bruto = f"{valor:,.2f}"
    return "R$ " + bruto.replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_relatorio(orcamento: OrcamentoMateriais, catalogo: dict[str, MaterialCatalogo]) -> str:
    linhas: list[str] = ["=== ORÇAMENTO DE MATERIAIS ===", "", "Itens"]

    for item in orcamento.itens:
        material = catalogo.get(item.cod_lista)
        if material is None:
            descricao = "CÓDIGO NÃO ENCONTRADO NO CATÁLOGO"
            tipo = "-"
            prioridade = "-"
        else:
            descricao = material.linha_viva or material.ativacao or "SEM DESCRIÇÃO"
            tipo = material.resumo or material.tipo_estr or "-"
            prioridade = material.prioridade if material.prioridade is not None else "-"

        linhas.append(
            f"- {item.cod_lista} | {descricao} | tipo: {tipo} | prioridade: {prioridade} | "
            f"{item.quantidade:g} x {formatar_moeda(item.preco_unitario)} = {formatar_moeda(item.subtotal)}"
        )

    linhas.extend(
        [
            "",
            f"Subtotal materiais: {formatar_moeda(orcamento.subtotal)}",
            (
                f"Imprevistos ({orcamento.taxa_imprevistos_percentual:.2f}%): "
                f"{formatar_moeda(orcamento.valor_imprevistos)}"
            ),
            f"TOTAL GERAL: {formatar_moeda(orcamento.total_geral)}",
        ]
    )
    return "\n".join(linhas)


def criar_parser_argumentos() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calcula orçamento de materiais")
    parser.add_argument("--catalogo-csv", type=Path, required=True, help="CSV do catálogo")
    parser.add_argument(
        "--orcamento-csv",
        type=Path,
        required=True,
        help="CSV com itens do orçamento (CODLISTA, QUANTIDADE, PRECO_UNITARIO)",
    )
    parser.add_argument(
        "--imprevistos",
        type=float,
        default=5.0,
        help="Percentual de imprevistos (padrão: 5)",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = criar_parser_argumentos().parse_args(list(argv) if argv is not None else None)

    catalogo = carregar_catalogo_materiais(args.catalogo_csv)
    itens = carregar_itens_orcamento(args.orcamento_csv)

    orcamento = OrcamentoMateriais(itens=itens, taxa_imprevistos_percentual=args.imprevistos)
    print(gerar_relatorio(orcamento, catalogo))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
