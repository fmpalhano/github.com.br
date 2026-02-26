from __future__ import annotations

import csv
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


CATALOGO_COLUNAS_OBRIGATORIAS = {
    "ATIVACAO",
    "LINHA_VIVA",
    "TIPOESTR",
    "CODLISTA",
    "RESUMO",
    "PRIORIDADE",
}

ITENS_COLUNAS_OBRIGATORIAS = {"CODLISTA", "QUANTIDADE", "PRECO_UNITARIO"}


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
    with caminho_csv.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        _validar_colunas(set(leitor.fieldnames or []), ITENS_COLUNAS_OBRIGATORIAS, caminho_csv)

        itens: list[ItemOrcamento] = []
        for linha in leitor:
            codigo = _normalizar_texto(linha["CODLISTA"])
            if not codigo:
                continue
            itens.append(
                ItemOrcamento(
                    cod_lista=codigo,
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


def gerar_relatorio_de_arquivos(
    caminho_catalogo: Path, caminho_orcamento: Path, imprevistos_percentual: float
) -> str:
    catalogo = carregar_catalogo_materiais(caminho_catalogo)
    itens = carregar_itens_orcamento(caminho_orcamento)
    orcamento = OrcamentoMateriais(itens=itens, taxa_imprevistos_percentual=imprevistos_percentual)
    return gerar_relatorio(orcamento, catalogo)


class AplicativoOrcamento(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Orçamento de Materiais")
        self.geometry("980x680")

        self.catalogo_var = tk.StringVar()
        self.orcamento_var = tk.StringVar()
        self.imprevistos_var = tk.StringVar(value="5")

        self._montar_interface()

    def _montar_interface(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Catálogo de materiais (CSV)").grid(row=0, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.catalogo_var).grid(
            row=1, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(container, text="Selecionar", command=self._selecionar_catalogo).grid(
            row=1, column=1, sticky="ew"
        )

        ttk.Label(container, text="Itens do orçamento (CSV)").grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )
        ttk.Entry(container, textvariable=self.orcamento_var).grid(
            row=3, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(container, text="Selecionar", command=self._selecionar_orcamento).grid(
            row=3, column=1, sticky="ew"
        )

        ttk.Label(container, text="Imprevistos (%)").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(container, textvariable=self.imprevistos_var, width=12).grid(
            row=5, column=0, sticky="w"
        )

        ttk.Button(container, text="Calcular orçamento", command=self._calcular).grid(
            row=5, column=1, sticky="ew"
        )

        self.relatorio_text = tk.Text(container, wrap="word")
        self.relatorio_text.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=(12, 0))

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.relatorio_text.yview)
        scrollbar.grid(row=6, column=2, sticky="ns", pady=(12, 0))
        self.relatorio_text.configure(yscrollcommand=scrollbar.set)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=0)
        container.rowconfigure(6, weight=1)

    def _selecionar_catalogo(self) -> None:
        arquivo = filedialog.askopenfilename(
            title="Selecione o catálogo de materiais",
            filetypes=[("CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        )
        if arquivo:
            self.catalogo_var.set(arquivo)

    def _selecionar_orcamento(self) -> None:
        arquivo = filedialog.askopenfilename(
            title="Selecione os itens do orçamento",
            filetypes=[("CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        )
        if arquivo:
            self.orcamento_var.set(arquivo)

    def _calcular(self) -> None:
        try:
            catalogo_path = Path(self.catalogo_var.get().strip())
            orcamento_path = Path(self.orcamento_var.get().strip())
            imprevistos = float(self.imprevistos_var.get().strip().replace(",", "."))

            if not catalogo_path.exists():
                raise ValueError("Selecione um catálogo CSV válido.")
            if not orcamento_path.exists():
                raise ValueError("Selecione um arquivo de orçamento CSV válido.")

            relatorio = gerar_relatorio_de_arquivos(catalogo_path, orcamento_path, imprevistos)
            self.relatorio_text.delete("1.0", tk.END)
            self.relatorio_text.insert(tk.END, relatorio)
        except Exception as exc:
            messagebox.showerror("Erro ao calcular orçamento", str(exc))


def main() -> int:
    app = AplicativoOrcamento()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
