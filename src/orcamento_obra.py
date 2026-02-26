from __future__ import annotations

import csv
import datetime as dt
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from src.material_storage import Material, MaterialStorage


SERVICOS_POR_TIPO: dict[str, list[dict[str, float | str]]] = {
    "Obra Elétrica": [
        {"nome": "Instalação de Poste", "codigo": "OBR.001", "valor_unitario": 52.0},
        {"nome": "Adequação de Rede", "codigo": "OBR.002", "valor_unitario": 64.0},
    ],
    "Ativação Elétrica": [
        {"nome": "Ligação de Cliente", "codigo": "ATV.001", "valor_unitario": 380.0},
        {"nome": "Ativação de Medidor", "codigo": "ATV.002", "valor_unitario": 420.0},
    ],
    "Lançamento de Cabo Elétrico": [
        {"nome": "Lançamento Aéreo", "codigo": "CAB.001", "valor_unitario": 1850.0},
        {"nome": "Lançamento Subterrâneo", "codigo": "CAB.002", "valor_unitario": 2200.0},
    ],
}


COLUNAS_EXPORTACAO = [
    "CHAVE",
    "DATA",
    "SUPERVISOR",
    "EQUIPE",
    "PEP",
    "DESCRIÇÃO OBRA",
    "ENCARREGADO",
    "TIPO SERVIÇO",
    "SERVIÇO",
    "MATERIAL",
    "QTD",
    "GPS POSTE",
    "SERVIÇO_REALIZADO",
    "QTD_REALIZADO",
    "VALID_EVIDÊNCIA",
    "RETORNO_META_Ñ_ALCANÇADA",
    "VALOR_REALIZADO",
    "VALOR_TOTAL",
    "VALOR_UNITÁRIO",
    "COD_SERVIÇO",
    "COD_SIMULADOR",
    "DISTANCIA",
    "CALC. TRANSPORTE",
    "DIFERENÇA",
]


@dataclass(frozen=True)
class ItemSelecionado:
    material: Material
    quantidade: float

    @property
    def total(self) -> float:
        return self.quantidade * self.material.valor_unitario


@dataclass(frozen=True)
class ResultadoOrcamento:
    chave: str
    data: str
    supervisor: str
    equipe: str
    pep: str
    descricao_obra: str
    encarregado: str
    tipo_servico: str
    servico: str
    cod_servico: str
    quantidade_clientes: int
    metros_ramal: float
    distancia_km: float
    metragem_final: float
    quantidade_servico: float
    valor_unitario_servico: float
    valor_servico: float
    valor_transporte: float
    itens_materiais: list[ItemSelecionado]

    @property
    def valor_materiais(self) -> float:
        return sum(item.total for item in self.itens_materiais)

    @property
    def valor_total(self) -> float:
        return self.valor_servico + self.valor_materiais + self.valor_transporte


def calcular_metragem_final(quantidade_clientes: int, metros_ramal: float) -> float:
    metragem_base = quantidade_clientes * metros_ramal
    return max(30.0, metragem_base) * 1.05


def formatar_moeda(valor: float) -> str:
    bruto = f"{valor:,.2f}"
    return "R$ " + bruto.replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_orcamento(
    chave: str,
    supervisor: str,
    equipe: str,
    pep: str,
    descricao_obra: str,
    encarregado: str,
    tipo_servico: str,
    servico: str,
    cod_servico: str,
    valor_unitario_servico: float,
    quantidade_clientes: int,
    metros_ramal: float,
    distancia_km: float,
    itens_materiais: list[ItemSelecionado],
) -> ResultadoOrcamento:
    if not tipo_servico:
        raise ValueError("Tipo de serviço é obrigatório.")
    if not servico:
        raise ValueError("Serviço é obrigatório.")

    metragem_final = calcular_metragem_final(quantidade_clientes, metros_ramal)
    if tipo_servico == "Lançamento de Cabo Elétrico":
        quantidade_servico = metragem_final / 1000.0
    elif tipo_servico == "Ativação Elétrica":
        quantidade_servico = float(quantidade_clientes)
    else:
        quantidade_servico = metragem_final

    valor_servico = quantidade_servico * valor_unitario_servico
    valor_transporte = distancia_km * 12.0

    return ResultadoOrcamento(
        chave=chave,
        data=dt.date.today().isoformat(),
        supervisor=supervisor,
        equipe=equipe,
        pep=pep,
        descricao_obra=descricao_obra,
        encarregado=encarregado,
        tipo_servico=tipo_servico,
        servico=servico,
        cod_servico=cod_servico,
        quantidade_clientes=quantidade_clientes,
        metros_ramal=metros_ramal,
        distancia_km=distancia_km,
        metragem_final=metragem_final,
        quantidade_servico=quantidade_servico,
        valor_unitario_servico=valor_unitario_servico,
        valor_servico=valor_servico,
        valor_transporte=valor_transporte,
        itens_materiais=itens_materiais,
    )


def gerar_preview(resultado: ResultadoOrcamento) -> str:
    linhas = [
        "=== ORÇAMENTO OBRA ELÉTRICA ===",
        f"Chave: {resultado.chave} | Data: {resultado.data}",
        f"Tipo Serviço: {resultado.tipo_servico} | Serviço: {resultado.servico}",
        f"Metragem final: {resultado.metragem_final:.2f} m",
        f"Valor Serviço: {formatar_moeda(resultado.valor_servico)}",
        f"Valor Transporte: {formatar_moeda(resultado.valor_transporte)}",
        "",
        "Materiais",
    ]
    if not resultado.itens_materiais:
        linhas.append("- Nenhum material selecionado")
    for item in resultado.itens_materiais:
        linhas.append(
            f"- {item.material.codigo} | {item.material.descricao} | {item.quantidade:g} {item.material.unidade} | "
            f"{formatar_moeda(item.material.valor_unitario)} | Total: {formatar_moeda(item.total)}"
        )
    linhas.extend(
        [
            "",
            f"Total Materiais: {formatar_moeda(resultado.valor_materiais)}",
            f"TOTAL GERAL: {formatar_moeda(resultado.valor_total)}",
        ]
    )
    return "\n".join(linhas)


def exportar_csv_padrao(resultado: ResultadoOrcamento, caminho: Path) -> None:
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=COLUNAS_EXPORTACAO)
        writer.writeheader()

        for item in resultado.itens_materiais or [ItemSelecionado(Material("", "", "", 0.0), 0.0)]:
            valor_realizado = item.total if item.material.codigo else 0.0
            diferenca = resultado.valor_total - valor_realizado
            writer.writerow(
                {
                    "CHAVE": resultado.chave,
                    "DATA": resultado.data,
                    "SUPERVISOR": resultado.supervisor,
                    "EQUIPE": resultado.equipe,
                    "PEP": resultado.pep,
                    "DESCRIÇÃO OBRA": resultado.descricao_obra,
                    "ENCARREGADO": resultado.encarregado,
                    "TIPO SERVIÇO": resultado.tipo_servico,
                    "SERVIÇO": resultado.servico,
                    "MATERIAL": item.material.descricao,
                    "QTD": f"{item.quantidade:.4f}",
                    "GPS POSTE": "",
                    "SERVIÇO_REALIZADO": resultado.servico,
                    "QTD_REALIZADO": f"{resultado.quantidade_servico:.4f}",
                    "VALID_EVIDÊNCIA": "PENDENTE",
                    "RETORNO_META_Ñ_ALCANÇADA": "",
                    "VALOR_REALIZADO": f"{valor_realizado:.2f}",
                    "VALOR_TOTAL": f"{resultado.valor_total:.2f}",
                    "VALOR_UNITÁRIO": f"{item.material.valor_unitario:.2f}",
                    "COD_SERVIÇO": item.material.cod_servico or resultado.cod_servico,
                    "COD_SIMULADOR": item.material.cod_simulador,
                    "DISTANCIA": f"{resultado.distancia_km:.2f}",
                    "CALC. TRANSPORTE": f"{resultado.valor_transporte:.2f}",
                    "DIFERENÇA": f"{diferenca:.2f}",
                }
            )


class MaterialEditor(tk.Toplevel):
    def __init__(self, master: tk.Tk, materiais: list[Material], on_save) -> None:
        super().__init__(master)
        self.title("Gerenciar Materiais (modo avançado)")
        self.geometry("980x480")
        self.transient(master)
        self.grab_set()
        self.on_save = on_save
        self.materiais = list(materiais)

        self.tree = ttk.Treeview(
            self,
            columns=("codigo", "descricao", "unidade", "valor", "cod_servico", "cod_simulador"),
            show="headings",
            height=12,
        )
        for col, txt, w in [
            ("codigo", "Código", 110),
            ("descricao", "Descrição", 280),
            ("unidade", "Unidade", 80),
            ("valor", "Valor", 100),
            ("cod_servico", "Cod Serviço", 120),
            ("cod_simulador", "Cod Simulador", 120),
        ]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="x", padx=8, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._carregar_selecao)

        form = ttk.Frame(self)
        form.pack(fill="x", padx=8)
        self.vars = {k: tk.StringVar() for k in ["codigo", "descricao", "unidade", "valor", "cod_servico", "cod_simulador"]}
        labels = ["codigo", "descricao", "unidade", "valor", "cod_servico", "cod_simulador"]
        for i, k in enumerate(labels):
            ttk.Label(form, text=k.replace("_", " ").title()).grid(row=0, column=i, sticky="w")
            ttk.Entry(form, textvariable=self.vars[k], width=20).grid(row=1, column=i, padx=(0, 6), sticky="w")

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", padx=8, pady=8)
        ttk.Button(botoes, text="Adicionar novo", command=self._adicionar).pack(side="left")
        ttk.Button(botoes, text="Editar existente", command=self._editar).pack(side="left", padx=(6, 0))
        ttk.Button(botoes, text="Remover", command=self._remover).pack(side="left", padx=(6, 0))
        ttk.Button(botoes, text="Salvar alterações", command=self._salvar_tudo).pack(side="left", padx=(6, 0))
        ttk.Button(botoes, text="Cancelar", command=self.destroy).pack(side="left", padx=(6, 0))

        self._recarregar_tree()

    def _recarregar_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for m in self.materiais:
            self.tree.insert("", "end", values=(m.codigo, m.descricao, m.unidade, f"{m.valor_unitario:.2f}", m.cod_servico, m.cod_simulador))

    def _carregar_selecao(self, _event=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        for idx, k in enumerate(["codigo", "descricao", "unidade", "valor", "cod_servico", "cod_simulador"]):
            self.vars[k].set(vals[idx])

    def _material_do_form(self) -> Material:
        codigo = self.vars["codigo"].get().strip()
        descricao = self.vars["descricao"].get().strip()
        unidade = self.vars["unidade"].get().strip()
        valor = float(self.vars["valor"].get().strip().replace(",", "."))
        cod_servico = self.vars["cod_servico"].get().strip()
        cod_simulador = self.vars["cod_simulador"].get().strip()
        if not codigo or not descricao or not unidade:
            raise ValueError("Código, descrição e unidade são obrigatórios.")
        return Material(codigo, descricao, unidade, valor, cod_servico, cod_simulador)

    def _adicionar(self) -> None:
        try:
            novo = self._material_do_form()
            if any(m.codigo == novo.codigo for m in self.materiais):
                raise ValueError("Código duplicado não permitido.")
            self.materiais.append(novo)
            self._recarregar_tree()
        except Exception as exc:
            messagebox.showerror("Editor", str(exc), parent=self)

    def _editar(self) -> None:
        try:
            atual = self._material_do_form()
            sel = self.tree.selection()
            if not sel:
                raise ValueError("Selecione uma linha para editar.")
            codigo_antigo = self.tree.item(sel[0], "values")[0]
            if atual.codigo != codigo_antigo and any(m.codigo == atual.codigo for m in self.materiais):
                raise ValueError("Código duplicado não permitido.")
            self.materiais = [atual if m.codigo == codigo_antigo else m for m in self.materiais]
            self._recarregar_tree()
        except Exception as exc:
            messagebox.showerror("Editor", str(exc), parent=self)

    def _remover(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        codigo = self.tree.item(sel[0], "values")[0]
        self.materiais = [m for m in self.materiais if m.codigo != codigo]
        self._recarregar_tree()

    def _salvar_tudo(self) -> None:
        self.on_save(self.materiais)
        self.destroy()


class AplicativoOrcamento(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sistema Profissional de Orçamento - Obra Elétrica")
        self.geometry("1360x860")

        self.storage = MaterialStorage(Path("data/materiais_base.json"))
        self.materiais = self.storage.carregar()
        self.quantidades: dict[str, str] = {m.codigo: "0" for m in self.materiais}
        self.selecoes: dict[str, tk.BooleanVar] = {}

        self.resultado_atual: ResultadoOrcamento | None = None

        self._setup_vars()
        self._montar_interface()

    def _setup_vars(self) -> None:
        self.tipo_servico_var = tk.StringVar()
        self.servico_var = tk.StringVar()
        self.busca_var = tk.StringVar()
        self.chave_var = tk.StringVar(value="ORC-001")
        self.supervisor_var = tk.StringVar()
        self.equipe_var = tk.StringVar()
        self.pep_var = tk.StringVar()
        self.descricao_obra_var = tk.StringVar()
        self.encarregado_var = tk.StringVar()
        self.clientes_var = tk.StringVar(value="1")
        self.metros_var = tk.StringVar(value="30")
        self.distancia_var = tk.StringVar(value="0")

    def _montar_interface(self) -> None:
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        dados = ttk.LabelFrame(root, text="Dados do orçamento", padding=8)
        dados.pack(fill="x")
        labels = [
            ("Chave", self.chave_var), ("Supervisor", self.supervisor_var), ("Equipe", self.equipe_var),
            ("PEP", self.pep_var), ("Descrição Obra", self.descricao_obra_var), ("Encarregado", self.encarregado_var),
            ("Qtd Clientes", self.clientes_var), ("Metros/Ramal", self.metros_var), ("Distância KM", self.distancia_var),
        ]
        for i, (txt, var) in enumerate(labels):
            ttk.Label(dados, text=txt).grid(row=(i//3)*2, column=i%3, sticky="w")
            ttk.Entry(dados, textvariable=var, width=38).grid(row=(i//3)*2+1, column=i%3, padx=6, pady=(0, 6), sticky="w")

        ttk.Label(dados, text="Tipo Serviço").grid(row=6, column=0, sticky="w")
        tipo_combo = ttk.Combobox(dados, textvariable=self.tipo_servico_var, state="readonly", values=list(SERVICOS_POR_TIPO.keys()), width=35)
        tipo_combo.grid(row=7, column=0, sticky="w", padx=6)
        tipo_combo.bind("<<ComboboxSelected>>", self._atualizar_servicos)

        ttk.Label(dados, text="Serviço").grid(row=6, column=1, sticky="w")
        self.servico_combo = ttk.Combobox(dados, textvariable=self.servico_var, state="readonly", width=35)
        self.servico_combo.grid(row=7, column=1, sticky="w", padx=6)

        mat_box = ttk.LabelFrame(root, text="Materiais da base interna", padding=8)
        mat_box.pack(fill="both", expand=True, pady=8)
        ttk.Label(mat_box, text="Pesquisa por código/descrição").pack(anchor="w")
        ttk.Entry(mat_box, textvariable=self.busca_var).pack(fill="x", pady=(0, 6))
        self.busca_var.trace_add("write", lambda *_: self._render_material_rows())

        self.canvas = tk.Canvas(mat_box, height=280)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(mat_box, orient="vertical", command=self.canvas.yview)
        sb.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=sb.set)
        self.material_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.material_frame, anchor="nw")
        self.material_frame.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        acoes = ttk.Frame(root)
        acoes.pack(fill="x")
        ttk.Button(acoes, text="Calcular Orçamento", command=self._calcular).pack(side="left")
        self.btn_export = ttk.Button(acoes, text="Exportar CSV", state="disabled", command=self._exportar)
        self.btn_export.pack(side="left", padx=6)
        ttk.Button(acoes, text="Limpar", command=self._limpar).pack(side="left", padx=6)
        ttk.Button(acoes, text="Gerenciar Materiais", command=self._gerenciar_materiais).pack(side="left", padx=6)

        preview = ttk.LabelFrame(root, text="Preview", padding=8)
        preview.pack(fill="both", expand=True, pady=(8, 0))
        self.preview_text = tk.Text(preview, wrap="word", height=12)
        self.preview_text.pack(fill="both", expand=True)

        self._render_material_rows()

    def _atualizar_servicos(self, _event=None) -> None:
        tipo = self.tipo_servico_var.get()
        opcoes = [s["nome"] for s in SERVICOS_POR_TIPO.get(tipo, [])]
        self.servico_combo["values"] = opcoes
        self.servico_var.set(opcoes[0] if opcoes else "")

    def _render_material_rows(self) -> None:
        for w in self.material_frame.winfo_children():
            w.destroy()

        headers = ["Sel", "Código", "Descrição", "Un", "Valor", "Qtd"]
        for c, h in enumerate(headers):
            ttk.Label(self.material_frame, text=h).grid(row=0, column=c, sticky="w")

        filtro = self.busca_var.get().strip().lower()
        visiveis = [m for m in self.materiais if not filtro or filtro in m.codigo.lower() or filtro in m.descricao.lower()]
        for i, m in enumerate(visiveis, start=1):
            if m.codigo not in self.selecoes:
                self.selecoes[m.codigo] = tk.BooleanVar(value=False)
            var_sel = self.selecoes[m.codigo]
            qtd_var = tk.StringVar(value=self.quantidades.get(m.codigo, "0"))
            qtd_var.trace_add("write", lambda *_a, codigo=m.codigo, v=qtd_var: self.quantidades.__setitem__(codigo, v.get()))

            ttk.Checkbutton(self.material_frame, variable=var_sel).grid(row=i, column=0, sticky="w")
            ttk.Label(self.material_frame, text=m.codigo, width=12).grid(row=i, column=1, sticky="w")
            ttk.Label(self.material_frame, text=m.descricao, width=55).grid(row=i, column=2, sticky="w")
            ttk.Label(self.material_frame, text=m.unidade, width=7).grid(row=i, column=3, sticky="w")
            ttk.Label(self.material_frame, text=formatar_moeda(m.valor_unitario), width=14).grid(row=i, column=4, sticky="w")
            ttk.Entry(self.material_frame, textvariable=qtd_var, width=10).grid(row=i, column=5, sticky="w")

    def _coletar_itens(self) -> list[ItemSelecionado]:
        itens = []
        mapa = {m.codigo: m for m in self.materiais}
        for codigo, sel in self.selecoes.items():
            if not sel.get() or codigo not in mapa:
                continue
            qtd = float(self.quantidades.get(codigo, "0").replace(",", "."))
            if qtd <= 0:
                raise ValueError(f"Quantidade inválida no material {codigo}.")
            itens.append(ItemSelecionado(mapa[codigo], qtd))
        return itens

    def _servico_escolhido(self) -> tuple[str, float]:
        tipo = self.tipo_servico_var.get()
        nome = self.servico_var.get()
        for item in SERVICOS_POR_TIPO.get(tipo, []):
            if item["nome"] == nome:
                return str(item["codigo"]), float(item["valor_unitario"])
        raise ValueError("Selecione tipo e serviço válidos.")

    def _calcular(self) -> None:
        try:
            cod_servico, valor_uni = self._servico_escolhido()
            self.resultado_atual = calcular_orcamento(
                chave=self.chave_var.get().strip() or "ORC-SEM-CHAVE",
                supervisor=self.supervisor_var.get().strip(),
                equipe=self.equipe_var.get().strip(),
                pep=self.pep_var.get().strip(),
                descricao_obra=self.descricao_obra_var.get().strip(),
                encarregado=self.encarregado_var.get().strip(),
                tipo_servico=self.tipo_servico_var.get().strip(),
                servico=self.servico_var.get().strip(),
                cod_servico=cod_servico,
                valor_unitario_servico=valor_uni,
                quantidade_clientes=int(self.clientes_var.get().strip()),
                metros_ramal=float(self.metros_var.get().strip().replace(",", ".")),
                distancia_km=float(self.distancia_var.get().strip().replace(",", ".")),
                itens_materiais=self._coletar_itens(),
            )
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, gerar_preview(self.resultado_atual))
            self.btn_export.configure(state="normal")
        except Exception as exc:
            self.btn_export.configure(state="disabled")
            messagebox.showerror("Cálculo", str(exc))

    def _exportar(self) -> None:
        if self.resultado_atual is None:
            messagebox.showwarning("Exportação", "Calcule antes de exportar.")
            return
        destino = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not destino:
            return
        exportar_csv_padrao(self.resultado_atual, Path(destino))
        messagebox.showinfo("Exportação", "CSV exportado com sucesso.")

    def _limpar(self) -> None:
        self.preview_text.delete("1.0", tk.END)
        self.resultado_atual = None
        self.btn_export.configure(state="disabled")
        for k in list(self.selecoes):
            self.selecoes[k].set(False)
            self.quantidades[k] = "0"
        self._render_material_rows()

    def _gerenciar_materiais(self) -> None:
        def salvar(materiais_editados: list[Material]) -> None:
            codigos = [m.codigo for m in materiais_editados]
            if len(codigos) != len(set(codigos)):
                raise ValueError("Existem códigos duplicados na base.")
            self.storage.salvar(materiais_editados)
            self.materiais = self.storage.carregar()
            for m in self.materiais:
                self.quantidades.setdefault(m.codigo, "0")
                self.selecoes.setdefault(m.codigo, tk.BooleanVar(value=False))
            self._render_material_rows()

        try:
            MaterialEditor(self, self.materiais, salvar)
        except Exception as exc:
            messagebox.showerror("Editor", str(exc))


def main() -> int:
    app = AplicativoOrcamento()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
