from __future__ import annotations

import csv
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from src.base_materiais import BASE_MATERIAIS, MaterialBase


@dataclass(frozen=True)
class ItemSelecionado:
    material: MaterialBase
    quantidade: float

    @property
    def total(self) -> float:
        return self.quantidade * self.material.valor_unitario


@dataclass(frozen=True)
class ResultadoOrcamento:
    tipo_servico: str
    quantidade_clientes: int
    metros_ramal: float
    distancia: float
    metragem_final: float
    quantidade_servico: float
    valor_unitario_servico: float
    valor_servico: float
    itens_materiais: list[ItemSelecionado]

    @property
    def valor_materiais(self) -> float:
        return sum(item.total for item in self.itens_materiais)

    @property
    def valor_total(self) -> float:
        return self.valor_servico + self.valor_materiais


SERVICOS = {
    "Ativação": 320.0,
    "Obra": 42.0,
    "Lançamento de Cabo": 1850.0,
}


def calcular_metragem_final(quantidade_clientes: int, metros_ramal: float) -> float:
    metragem_base = quantidade_clientes * metros_ramal
    return max(30.0, metragem_base) * 1.05


def formatar_moeda(valor: float) -> str:
    bruto = f"{valor:,.2f}"
    return "R$ " + bruto.replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_orcamento(
    tipo_servico: str,
    quantidade_clientes: int,
    metros_ramal: float,
    distancia: float,
    itens_materiais: list[ItemSelecionado],
) -> ResultadoOrcamento:
    if tipo_servico not in SERVICOS:
        raise ValueError("Selecione um tipo de serviço válido.")

    metragem_final = calcular_metragem_final(quantidade_clientes, metros_ramal)

    if tipo_servico == "Ativação":
        quantidade_servico = float(quantidade_clientes)
    elif tipo_servico == "Obra":
        quantidade_servico = metragem_final
    else:
        quantidade_servico = metragem_final / 1000.0

    valor_unitario_servico = SERVICOS[tipo_servico]
    valor_servico = quantidade_servico * valor_unitario_servico

    return ResultadoOrcamento(
        tipo_servico=tipo_servico,
        quantidade_clientes=quantidade_clientes,
        metros_ramal=metros_ramal,
        distancia=distancia,
        metragem_final=metragem_final,
        quantidade_servico=quantidade_servico,
        valor_unitario_servico=valor_unitario_servico,
        valor_servico=valor_servico,
        itens_materiais=itens_materiais,
    )


def gerar_preview(resultado: ResultadoOrcamento) -> str:
    linhas = [
        "=== ORÇAMENTO TELECOM ===",
        "",
        f"Tipo de serviço: {resultado.tipo_servico}",
        f"Quantidade de clientes: {resultado.quantidade_clientes}",
        f"Metros por ramal: {resultado.metros_ramal:.2f}",
        f"Distância informada: {resultado.distancia:.2f}",
        f"Metragem final (com mínimo + 5%): {resultado.metragem_final:.2f} m",
        "",
        "Serviço",
        (
            f"- Quantidade calculada: {resultado.quantidade_servico:.4f} | "
            f"Valor unitário: {formatar_moeda(resultado.valor_unitario_servico)} | "
            f"Total serviço: {formatar_moeda(resultado.valor_servico)}"
        ),
        "",
        "Materiais selecionados",
    ]

    if not resultado.itens_materiais:
        linhas.append("- Nenhum material selecionado")
    else:
        for item in resultado.itens_materiais:
            linhas.append(
                f"- {item.material.codigo} | {item.material.descricao} | {item.quantidade:g} {item.material.unidade} "
                f"x {formatar_moeda(item.material.valor_unitario)} = {formatar_moeda(item.total)}"
            )

    linhas.extend(
        [
            "",
            f"Total serviço: {formatar_moeda(resultado.valor_servico)}",
            f"Total materiais: {formatar_moeda(resultado.valor_materiais)}",
            f"TOTAL GERAL: {formatar_moeda(resultado.valor_total)}",
        ]
    )

    return "\n".join(linhas)


def exportar_orcamento_csv(resultado: ResultadoOrcamento, caminho: Path) -> None:
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)

        writer.writerow(["DADOS DO SERVIÇO"])
        writer.writerow(["Tipo de Serviço", resultado.tipo_servico])
        writer.writerow(["Quantidade de Clientes", resultado.quantidade_clientes])
        writer.writerow(["Metros por Ramal", f"{resultado.metros_ramal:.2f}"])
        writer.writerow(["Distância", f"{resultado.distancia:.2f}"])
        writer.writerow(["Metragem Final (m)", f"{resultado.metragem_final:.2f}"])
        writer.writerow(["Quantidade de Serviço", f"{resultado.quantidade_servico:.4f}"])
        writer.writerow(["Valor Unitário Serviço", f"{resultado.valor_unitario_servico:.2f}"])
        writer.writerow(["Valor Serviço", f"{resultado.valor_servico:.2f}"])
        writer.writerow([])

        writer.writerow(["MATERIAIS SELECIONADOS"])
        writer.writerow(
            ["Código", "Descrição", "Unidade", "Quantidade", "Valor Unitário", "Total Item"]
        )

        for item in resultado.itens_materiais:
            writer.writerow(
                [
                    item.material.codigo,
                    item.material.descricao,
                    item.material.unidade,
                    f"{item.quantidade:.4f}",
                    f"{item.material.valor_unitario:.2f}",
                    f"{item.total:.2f}",
                ]
            )

        writer.writerow([])
        writer.writerow(["Total Materiais", f"{resultado.valor_materiais:.2f}"])
        writer.writerow(["Total Geral", f"{resultado.valor_total:.2f}"])


class LinhaMaterialUI:
    def __init__(self, parent: ttk.Frame, material: MaterialBase, row_index: int) -> None:
        self.material = material
        self.selecionado_var = tk.BooleanVar(value=False)
        self.quantidade_var = tk.StringVar(value="0")

        self.check = ttk.Checkbutton(parent, variable=self.selecionado_var)
        self.check.grid(row=row_index, column=0, sticky="w")

        ttk.Label(parent, text=material.codigo, width=12).grid(row=row_index, column=1, sticky="w")
        ttk.Label(parent, text=material.descricao, width=42).grid(row=row_index, column=2, sticky="w")
        ttk.Label(parent, text=material.unidade, width=8).grid(row=row_index, column=3, sticky="w")
        ttk.Label(parent, text=formatar_moeda(material.valor_unitario), width=14).grid(
            row=row_index, column=4, sticky="w"
        )
        ttk.Entry(parent, textvariable=self.quantidade_var, width=10).grid(
            row=row_index, column=5, sticky="w"
        )

    def para_item(self) -> ItemSelecionado | None:
        if not self.selecionado_var.get():
            return None

        quantidade_texto = self.quantidade_var.get().strip().replace(",", ".")
        quantidade = float(quantidade_texto)
        if quantidade <= 0:
            raise ValueError(f"Quantidade inválida para material {self.material.codigo}.")

        return ItemSelecionado(material=self.material, quantidade=quantidade)


class AplicativoOrcamento(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sistema de Orçamento Telecom")
        self.geometry("1200x760")

        self.tipo_servico_var = tk.StringVar(value="")
        self.qtd_clientes_var = tk.StringVar(value="1")
        self.metros_ramal_var = tk.StringVar(value="30")
        self.distancia_var = tk.StringVar(value="0")

        self.linhas_materiais: list[LinhaMaterialUI] = []
        self.resultado_atual: ResultadoOrcamento | None = None

        self._montar_interface()

    def _montar_interface(self) -> None:
        raiz = ttk.Frame(self, padding=10)
        raiz.pack(fill="both", expand=True)

        topo = ttk.LabelFrame(raiz, text="Dados do Serviço", padding=10)
        topo.pack(fill="x")

        ttk.Label(topo, text="Tipo de Serviço").grid(row=0, column=0, sticky="w")
        combo = ttk.Combobox(
            topo,
            textvariable=self.tipo_servico_var,
            values=list(SERVICOS.keys()),
            state="readonly",
            width=24,
        )
        combo.grid(row=1, column=0, padx=(0, 12), sticky="w")

        ttk.Label(topo, text="Quantidade de Clientes").grid(row=0, column=1, sticky="w")
        ttk.Entry(topo, textvariable=self.qtd_clientes_var, width=16).grid(
            row=1, column=1, padx=(0, 12), sticky="w"
        )

        ttk.Label(topo, text="Metros por Ramal").grid(row=0, column=2, sticky="w")
        ttk.Entry(topo, textvariable=self.metros_ramal_var, width=16).grid(
            row=1, column=2, padx=(0, 12), sticky="w"
        )

        ttk.Label(topo, text="Distância").grid(row=0, column=3, sticky="w")
        ttk.Entry(topo, textvariable=self.distancia_var, width=16).grid(row=1, column=3, sticky="w")

        materiais_box = ttk.LabelFrame(raiz, text="Base Interna de Materiais", padding=8)
        materiais_box.pack(fill="both", expand=True, pady=(8, 8))

        canvas = tk.Canvas(materiais_box, height=300)
        scrollbar = ttk.Scrollbar(materiais_box, orient="vertical", command=canvas.yview)
        quadro_lista = ttk.Frame(canvas)

        quadro_lista.bind(
            "<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=quadro_lista, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(quadro_lista, text="Sel", width=4).grid(row=0, column=0, sticky="w")
        ttk.Label(quadro_lista, text="Código", width=12).grid(row=0, column=1, sticky="w")
        ttk.Label(quadro_lista, text="Descrição", width=42).grid(row=0, column=2, sticky="w")
        ttk.Label(quadro_lista, text="Un", width=8).grid(row=0, column=3, sticky="w")
        ttk.Label(quadro_lista, text="Valor Unitário", width=14).grid(row=0, column=4, sticky="w")
        ttk.Label(quadro_lista, text="Quantidade", width=12).grid(row=0, column=5, sticky="w")

        for idx, material in enumerate(BASE_MATERIAIS, start=1):
            linha = LinhaMaterialUI(quadro_lista, material, idx)
            self.linhas_materiais.append(linha)

        acoes = ttk.Frame(raiz)
        acoes.pack(fill="x", pady=(0, 8))

        ttk.Button(acoes, text="Calcular Orçamento", command=self._calcular).pack(side="left")
        self.botao_exportar = ttk.Button(
            acoes, text="Exportar para Planilha", command=self._exportar, state="disabled"
        )
        self.botao_exportar.pack(side="left", padx=(8, 0))
        ttk.Button(acoes, text="Limpar", command=self._limpar).pack(side="left", padx=(8, 0))

        preview_box = ttk.LabelFrame(raiz, text="Preview do Orçamento", padding=8)
        preview_box.pack(fill="both", expand=True)

        self.preview_text = tk.Text(preview_box, wrap="word", height=12)
        self.preview_text.pack(side="left", fill="both", expand=True)
        preview_scroll = ttk.Scrollbar(preview_box, orient="vertical", command=self.preview_text.yview)
        preview_scroll.pack(side="right", fill="y")
        self.preview_text.configure(yscrollcommand=preview_scroll.set)

    def _coletar_itens(self) -> list[ItemSelecionado]:
        itens: list[ItemSelecionado] = []
        for linha in self.linhas_materiais:
            item = linha.para_item()
            if item is not None:
                itens.append(item)
        return itens

    def _calcular(self) -> None:
        try:
            tipo_servico = self.tipo_servico_var.get().strip()
            if not tipo_servico:
                raise ValueError("Selecione um tipo de serviço antes de calcular.")

            quantidade_clientes = int(self.qtd_clientes_var.get().strip())
            metros_ramal = float(self.metros_ramal_var.get().strip().replace(",", "."))
            distancia = float(self.distancia_var.get().strip().replace(",", "."))

            if quantidade_clientes <= 0:
                raise ValueError("Quantidade de clientes deve ser maior que zero.")
            if metros_ramal <= 0:
                raise ValueError("Metros por ramal deve ser maior que zero.")

            itens = self._coletar_itens()

            self.resultado_atual = calcular_orcamento(
                tipo_servico=tipo_servico,
                quantidade_clientes=quantidade_clientes,
                metros_ramal=metros_ramal,
                distancia=distancia,
                itens_materiais=itens,
            )

            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, gerar_preview(self.resultado_atual))
            self.botao_exportar.configure(state="normal")
        except Exception as exc:
            self.botao_exportar.configure(state="disabled")
            messagebox.showerror("Erro no cálculo", str(exc))

    def _exportar(self) -> None:
        if self.resultado_atual is None:
            messagebox.showwarning("Exportação", "Calcule o orçamento antes de exportar.")
            return

        caminho = filedialog.asksaveasfilename(
            title="Exportar orçamento",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not caminho:
            return

        try:
            exportar_orcamento_csv(self.resultado_atual, Path(caminho))
            messagebox.showinfo("Exportação", "Planilha exportada com sucesso.")
        except Exception as exc:
            messagebox.showerror("Erro na exportação", str(exc))

    def _limpar(self) -> None:
        self.tipo_servico_var.set("")
        self.qtd_clientes_var.set("1")
        self.metros_ramal_var.set("30")
        self.distancia_var.set("0")

        for linha in self.linhas_materiais:
            linha.selecionado_var.set(False)
            linha.quantidade_var.set("0")

        self.resultado_atual = None
        self.botao_exportar.configure(state="disabled")
        self.preview_text.delete("1.0", tk.END)


def main() -> int:
    app = AplicativoOrcamento()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
