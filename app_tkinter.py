import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from datetime import datetime


METRAGEM_MINIMA = 30.0
SANGRIA_PERCENTUAL = 0.05
TARIFA_TRANSPORTE_KM = 3.5


@dataclass
class Servico:
    id: str
    nome: str
    valor_unitario: float


@dataclass
class Material:
    codigo: str
    nome: str
    unidade: str
    valor_unitario: float


SERVICOS_POR_TIPO = {
    "Ativação": [
        Servico("ativacao_residencial", "Ativação Residencial", 5.0),
        Servico("ativacao_empresarial", "Ativação Empresarial", 8.5),
    ],
    "Obra": [
        Servico("obra_rede", "Obra de Rede", 11.0),
        Servico("obra_reforma", "Reforma de Rede", 13.5),
    ],
    "Lançamento de Cabo": [
        Servico("lancamento_aereo", "Lançamento Aéreo", 950.0),
        Servico("lancamento_subterraneo", "Lançamento Subterrâneo", 1350.0),
    ],
}

MATERIAIS = [
    Material("134210001", "SAPATILHA PESAD AC GF 9,5MM 3160DAN", "UN", 22.0),
    Material("134860002", "PORCA OLH AC ZC 38X45X16MM 5000DAN", "UN", 18.0),
    Material("134740023", "PARAFUSO OLHAL ACO M16 X 250MM", "UN", 35.0),
    Material("134510006", "ELETRODUTO PVC RIG 3/4 3M BSP PT", "UN", 29.0),
    Material("124120002", "CONECT DER PERF POL/CU 120X25-120MM 1KV", "UN", 44.0),
    Material("124010017", "CONECT CUN RAM CU/EST TIPO VII BR/VM", "UN", 12.0),
    Material("124140026", "CONEC CUN AT CB/HT CU 6-16MM2 16MM PDE", "UN", 38.0),
    Material("134830013", "ARRUELA QUAD AC ZC 38X38X3MM F Ø18MM", "UN", 6.0),
    Material("134300002", "ALCA PREF DT CA/CAA 1/0AWG 9,15-10,25 AM", "UN", 16.0),
    Material("134610002", "HASTE AT CANT ACO 25X25X5MM 2,4M", "UN", 120.0),
    Material("135220009", "ABRACADEIRA CINT 7,6X250MM NYL 6.6 PT", "UN", 3.5),
    Material("124030041", "CONECTOR ESTRIBO AL 1/0 A 3/0", "UN", 27.0),
]


class AppOrcamento:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Orçamento e Pedido de Materiais")
        self.root.geometry("1240x860")

        self.pi_por_obra: dict[str, float] = {}

        self.obra_var = tk.StringVar()
        self.pi_var = tk.StringVar()
        self.tipo_var = tk.StringVar()
        self.servico_var = tk.StringVar()
        self.qtd_clientes_var = tk.StringVar()
        self.metros_ramal_var = tk.StringVar()
        self.distancia_km_var = tk.StringVar()

        self.metragem_total_var = tk.StringVar()
        self.metragem_sangria_var = tk.StringVar()
        self.valor_servico_var = tk.StringVar()
        self.valor_materiais_var = tk.StringVar()
        self.valor_transporte_var = tk.StringVar()
        self.valor_total_var = tk.StringVar()
        self.saldo_pi_var = tk.StringVar(value="Saldo P.I: -")

        self.material_vars = {}

        self._montar_layout()

    def _montar_layout(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Simulador de Orçamento + Pedido", font=("Arial", 16, "bold")).pack(anchor="w")

        top_hud = ttk.Frame(container)
        top_hud.pack(fill="x", pady=(8, 10))

        ttk.Button(top_hud, text="Pedido", command=self.abrir_pedido).pack(side="left", padx=(0, 8))
        ttk.Button(top_hud, text="Calcular Orçamento", command=self.calcular_orcamento).pack(side="left", padx=(0, 8))
        ttk.Button(top_hud, text="Limpar", command=self.limpar).pack(side="left", padx=(0, 8))
        ttk.Label(top_hud, textvariable=self.saldo_pi_var, font=("Arial", 11, "bold")).pack(side="right")

        obra_frame = ttk.LabelFrame(container, text="Obra e P.I (fixo por obra)", padding=10)
        obra_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(obra_frame, text="Obra:").grid(row=0, column=0, sticky="w")
        ttk.Entry(obra_frame, textvariable=self.obra_var, width=24).grid(row=0, column=1, padx=6)
        ttk.Label(obra_frame, text="P.I disponível (R$):").grid(row=0, column=2, sticky="w")
        ttk.Entry(obra_frame, textvariable=self.pi_var, width=18).grid(row=0, column=3, padx=6)
        ttk.Button(obra_frame, text="Fixar P.I da Obra", command=self.fixar_pi_da_obra).grid(row=0, column=4, padx=6)

        dados = ttk.LabelFrame(container, text="Dados do orçamento", padding=10)
        dados.pack(fill="x", pady=(0, 8))

        ttk.Label(dados, text="Tipo Serviço").grid(row=0, column=0, sticky="w")
        self.tipo_combo = ttk.Combobox(dados, textvariable=self.tipo_var, values=list(SERVICOS_POR_TIPO.keys()), state="readonly", width=25)
        self.tipo_combo.grid(row=1, column=0, padx=4, sticky="ew")
        self.tipo_combo.bind("<<ComboboxSelected>>", self.on_tipo_change)

        ttk.Label(dados, text="Serviço específico").grid(row=0, column=1, sticky="w")
        self.servico_combo = ttk.Combobox(dados, textvariable=self.servico_var, state="readonly", width=34)
        self.servico_combo.grid(row=1, column=1, padx=4, sticky="ew")

        ttk.Label(dados, text="Qtd Clientes").grid(row=0, column=2, sticky="w")
        ttk.Entry(dados, textvariable=self.qtd_clientes_var, width=14).grid(row=1, column=2, padx=4)
        ttk.Label(dados, text="Metros/Ramal").grid(row=0, column=3, sticky="w")
        ttk.Entry(dados, textvariable=self.metros_ramal_var, width=14).grid(row=1, column=3, padx=4)
        ttk.Label(dados, text="Distância KM").grid(row=0, column=4, sticky="w")
        ttk.Entry(dados, textvariable=self.distancia_km_var, width=14).grid(row=1, column=4, padx=4)

        mat_frame = ttk.LabelFrame(container, text="Materiais", padding=10)
        mat_frame.pack(fill="both", expand=True, pady=(0, 8))

        headers = ["Sel", "Código", "Descrição", "UND", "Valor Unit.", "Qtd"]
        for c, h in enumerate(headers):
            ttk.Label(mat_frame, text=h, font=("Arial", 9, "bold")).grid(row=0, column=c, sticky="w", padx=3)

        for idx, material in enumerate(MATERIAIS, start=1):
            sel = tk.BooleanVar(value=False)
            qtd = tk.StringVar(value="0")
            valor = tk.StringVar(value=f"{material.valor_unitario:.2f}")
            ttk.Checkbutton(mat_frame, variable=sel).grid(row=idx, column=0)
            ttk.Label(mat_frame, text=material.codigo).grid(row=idx, column=1, sticky="w")
            ttk.Label(mat_frame, text=material.nome).grid(row=idx, column=2, sticky="w")
            ttk.Label(mat_frame, text=material.unidade).grid(row=idx, column=3, sticky="w")
            ttk.Entry(mat_frame, textvariable=valor, width=10).grid(row=idx, column=4)
            ttk.Entry(mat_frame, textvariable=qtd, width=10).grid(row=idx, column=5)
            self.material_vars[material.codigo] = {"sel": sel, "qtd": qtd, "valor": valor, "material": material}

        res = ttk.LabelFrame(container, text="Resultado financeiro", padding=10)
        res.pack(fill="x")

        campos = [
            ("Metragem Total", self.metragem_total_var),
            ("Metragem com Sangria", self.metragem_sangria_var),
            ("Valor Serviço", self.valor_servico_var),
            ("Valor Materiais", self.valor_materiais_var),
            ("Valor Transporte", self.valor_transporte_var),
            ("Valor Total", self.valor_total_var),
        ]
        for i, (lbl, var) in enumerate(campos):
            ttk.Label(res, text=lbl).grid(row=i // 3, column=(i % 3) * 2, sticky="w", padx=4, pady=2)
            ttk.Entry(res, textvariable=var, state="readonly", width=24).grid(row=i // 3, column=(i % 3) * 2 + 1, padx=4, pady=2)

    def on_tipo_change(self, _=None) -> None:
        tipo = self.tipo_var.get()
        self.servico_combo["values"] = [s.nome for s in SERVICOS_POR_TIPO.get(tipo, [])]
        self.servico_var.set("")

    @staticmethod
    def parse_num(v: str, campo: str) -> float:
        texto = (v or "").strip().replace(".", "").replace(",", ".")
        if not texto:
            raise ValueError(f"Preencha {campo}.")
        return float(texto)

    @staticmethod
    def money(v: float) -> str:
        return f"R$ {v:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

    def fixar_pi_da_obra(self) -> None:
        try:
            obra = self.obra_var.get().strip()
            if not obra:
                raise ValueError("Informe o identificador da obra.")
            pi = self.parse_num(self.pi_var.get(), "P.I")
            if pi <= 0:
                raise ValueError("P.I deve ser maior que zero.")
            self.pi_por_obra[obra] = pi
            messagebox.showinfo("P.I", f"P.I de {self.money(pi)} fixado para a obra '{obra}'.")
            self.atualizar_saldo_pi()
        except ValueError as e:
            messagebox.showerror("Validação", str(e))

    def obter_servico(self) -> Servico:
        for s in SERVICOS_POR_TIPO.get(self.tipo_var.get(), []):
            if s.nome == self.servico_var.get():
                return s
        raise ValueError("Selecione um serviço válido.")

    def calcular_materiais(self) -> tuple[list[dict], float]:
        itens = []
        total = 0.0
        for data in self.material_vars.values():
            if not data["sel"].get():
                continue
            qtd = self.parse_num(data["qtd"].get(), f"quantidade de {data['material'].codigo}")
            valor = self.parse_num(data["valor"].get(), f"valor de {data['material'].codigo}")
            subtotal = qtd * valor
            itens.append({
                "codigo": data["material"].codigo,
                "descricao": data["material"].nome,
                "unidade": data["material"].unidade,
                "qtd": qtd,
                "valor_unitario": valor,
                "subtotal": subtotal,
            })
            total += subtotal
        return itens, total

    def calcular_orcamento(self) -> None:
        try:
            if not self.tipo_var.get():
                raise ValueError("Selecione tipo de serviço.")
            servico = self.obter_servico()
            qtd_clientes = self.parse_num(self.qtd_clientes_var.get(), "Quantidade de clientes")
            metros_ramal = self.parse_num(self.metros_ramal_var.get(), "Metros por ramal")
            distancia = 0.0 if not self.distancia_km_var.get().strip() else self.parse_num(self.distancia_km_var.get(), "Distância")

            if qtd_clientes <= 0 or metros_ramal <= 0 or distancia < 0:
                raise ValueError("Valores inválidos no orçamento.")

            metragem_base = qtd_clientes * metros_ramal
            metragem_final = max(METRAGEM_MINIMA, metragem_base)
            metragem_sangria = metragem_final * (1 + SANGRIA_PERCENTUAL)

            if self.tipo_var.get() == "Lançamento de Cabo":
                valor_servico = (metragem_sangria / 1000.0) * servico.valor_unitario
            else:
                valor_servico = metragem_sangria * servico.valor_unitario

            _, valor_materiais = self.calcular_materiais()
            valor_transporte = distancia * TARIFA_TRANSPORTE_KM
            valor_total = valor_servico + valor_materiais + valor_transporte

            self.metragem_total_var.set(f"{metragem_final:.2f}")
            self.metragem_sangria_var.set(f"{metragem_sangria:.2f}")
            self.valor_servico_var.set(self.money(valor_servico))
            self.valor_materiais_var.set(self.money(valor_materiais))
            self.valor_transporte_var.set(self.money(valor_transporte))
            self.valor_total_var.set(self.money(valor_total))
            self.atualizar_saldo_pi()
            messagebox.showinfo("Sucesso", "Orçamento calculado.")
        except ValueError as e:
            messagebox.showerror("Validação", str(e))

    def valor_total_num(self) -> float:
        if not self.valor_total_var.get():
            return 0.0
        texto = self.valor_total_var.get().replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(texto)

    def atualizar_saldo_pi(self) -> None:
        obra = self.obra_var.get().strip()
        if not obra or obra not in self.pi_por_obra:
            self.saldo_pi_var.set("Saldo P.I: informe/fixe o P.I da obra")
            return
        total = self.valor_total_num()
        saldo = self.pi_por_obra[obra] - total
        self.saldo_pi_var.set(f"Saldo P.I ({obra}): {self.money(saldo)}")

    def abrir_pedido(self) -> None:
        if not self.valor_total_var.get():
            messagebox.showwarning("Pedido", "Calcule o orçamento antes de abrir o Pedido.")
            return

        obra = self.obra_var.get().strip()
        if not obra or obra not in self.pi_por_obra:
            messagebox.showwarning("Pedido", "Fixe o P.I da obra antes de gerar o Pedido.")
            return

        itens, total_materiais = self.calcular_materiais()
        if not itens:
            messagebox.showwarning("Pedido", "Selecione ao menos um material para gerar o Pedido.")
            return

        valor_total = self.valor_total_num()
        pi = self.pi_por_obra[obra]
        saldo = pi - valor_total

        tela = tk.Toplevel(self.root)
        tela.title("Pedido / Romaneio de Materiais")
        tela.geometry("1200x850")

        outer = ttk.Frame(tela, padding=10)
        outer.pack(fill="both", expand=True)

        ttk.Label(
            outer,
            text='GRUPO SETUP\nAV. RICARDO LEÔNIDAS RIBAS, 115\nRIO GRANDE DO SUL-RS\nCNPJ: 09.249662/0006.89',
            font=("Arial", 10, "bold"),
            justify="center",
        ).pack(fill="x")

        ttk.Label(outer, text="ROMANEIO DE MATERIAIS", font=("Arial", 13, "bold")).pack(fill="x", pady=(8, 8))

        info = ttk.Frame(outer)
        info.pack(fill="x")
        ttk.Label(info, text=f"Solicitante: ").grid(row=0, column=0, sticky="w")
        ttk.Label(info, text=f"Data Solicitação: {datetime.now().strftime('%d/%m/%Y')}").grid(row=0, column=1, sticky="w", padx=20)
        ttk.Label(info, text=f"Obra: {obra}").grid(row=1, column=0, sticky="w")
        ttk.Label(info, text=f"Tipo Serviço: {self.tipo_var.get()} | Serviço: {self.servico_var.get()}").grid(row=1, column=1, sticky="w", padx=20)
        ttk.Label(info, text=f"P.I fixado: {self.money(pi)}").grid(row=2, column=0, sticky="w")
        ttk.Label(info, text=f"Valor do orçamento: {self.money(valor_total)}").grid(row=2, column=1, sticky="w", padx=20)
        ttk.Label(info, text=f"Valor materiais pedido: {self.money(total_materiais)}").grid(row=3, column=0, sticky="w")
        ttk.Label(info, text=f"Saldo P.I após pedido: {self.money(saldo)}").grid(row=3, column=1, sticky="w", padx=20)

        tabela_frame = ttk.Frame(outer)
        tabela_frame.pack(fill="both", expand=True, pady=12)

        cols = ("cod", "desc", "und", "qtd")
        tree = ttk.Treeview(tabela_frame, columns=cols, show="headings", height=14)
        tree.heading("cod", text="COD. MAT")
        tree.heading("desc", text="DESC MATERIAL")
        tree.heading("und", text="UND")
        tree.heading("qtd", text="QNTD")
        tree.column("cod", width=130)
        tree.column("desc", width=700)
        tree.column("und", width=80)
        tree.column("qtd", width=100)
        tree.pack(side="left", fill="both", expand=True)

        sc = ttk.Scrollbar(tabela_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sc.set)
        sc.pack(side="right", fill="y")

        for item in itens:
            tree.insert("", "end", values=(item["codigo"], item["descricao"], item["unidade"], f"{item['qtd']:.2f}"))

        rodape = ttk.LabelFrame(outer, text="Assinaturas e controle (template)", padding=10)
        rodape.pack(fill="x")

        texto_template = (
            "EXPEDIÇÃO / DEVOLUÇÃO\n"
            "SEPARADOR: ___________________    RECEBEDOR: ___________________\n"
            "ENTREGADOR: ___________________   ENTREGADOR: ___________________\n"
            "RECEBEDOR: ___________________    DATA: ____/____/______\n"
            "MOTIVO DA DEVOLUÇÃO (OBRIGATÓRIO):\n"
            "(   ) ALTERAÇÃO DE PROJETO   (   ) OBRA CONCLUÍDA   (   ) MUDANÇA DE PROGRAMAÇÃO\n"
            "(   ) ANÁLISE NA LISTA TÉCNICA (   ) CAVA EM ROCHA  (   ) SEM ACESSO\n"
            "(   ) NECESSIDADE DE PODA     (   ) SAQUE PARCIAL    (   ) OUTROS"
        )
        ttk.Label(rodape, text=texto_template, justify="left").pack(anchor="w")

    def limpar(self) -> None:
        self.tipo_var.set("")
        self.servico_var.set("")
        self.qtd_clientes_var.set("")
        self.metros_ramal_var.set("")
        self.distancia_km_var.set("")
        self.metragem_total_var.set("")
        self.metragem_sangria_var.set("")
        self.valor_servico_var.set("")
        self.valor_materiais_var.set("")
        self.valor_transporte_var.set("")
        self.valor_total_var.set("")
        self.saldo_pi_var.set("Saldo P.I: -")
        for data in self.material_vars.values():
            data["sel"].set(False)
            data["qtd"].set("0")


def main() -> None:
    root = tk.Tk()
    app = AppOrcamento(root)
    root.minsize(1180, 780)
    root.mainloop()


if __name__ == "__main__":
    main()
