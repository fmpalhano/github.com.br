#!/usr/bin/env python3
"""Exportador de planilhas para ingestão no SIPROG."""

from __future__ import annotations

import argparse
import re
import threading
import traceback
import warnings
from queue import Empty, Queue
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from tkinter import Tk, Toplevel, END, StringVar, TclError, filedialog
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

if TYPE_CHECKING:
    import pandas as pd

DEFAULT_OUTPUT = "exportacao_siprog.xlsx"
DEFAULT_DATA_COLUMN = "DATA PROGRAMAÇÃO"
DEFAULT_STATUS_COLUMN = "STATUS SAP"
DEFAULT_WORKSHEET = "PROGRAMACAO_OBRAS"

REQUIRED_COLUMNS = [
    "CAPEX/OPEX",
    "NOTA PROJETO - SOMENTE CAPEX",
    "NOTA CLIENTE - SOMENTE CAPEX",
    "NOME OBRA - SOMENTE CAPEX",
    "COD. PROGRAMAÇÃO - SOMENTE OPEX",
    "EQP. NOVO? – SOMENTE OPEX",
    "SE / ORIGEM LTDA – SOMENTE OPEX",
    "LOCAL INSTAL. – SOMENTE OPEX",
    "DATA INSPEÇÃO – SOMENTE OPEX",
    "ORDEM INSPEÇÃO – SOMENTE OPEX",
    "PRIORIDADE – SOMENTE OPEX",
    "CLASSE – SOMENTE OPEX",
    "DESCRIÇÃO ANOMALIA – SOMENTE OPEX",
    "REGIONAL",
    "PARCEIRA",
    "EQUIPE",
    "REFERÊNCIA",
    "PRAZO CONCLUSÃO",
    "DATA PROGRAMAÇÃO",
    "QUANTIDADES DIAS",
    "ELEMENTO PEP – SOMENTE CAPEX",
    "ORDEM SERVIÇO – SOMENTE OPEX",
    "ORÇAMENTO MAT.",
    "ORÇAMENTO MO",
    "VALOR MÃO DE OBRA PROGRAMADA",
    "TURNO",
    "COM RECLAMAÇÃO?",
    "ORIGEM RECLAMAÇÃO",
    "TIPO SERVIÇO",
    "TEM RESTRIÇÃO?",
    "OBRA VALIDADA EM CAMPO?",
    "STATUS SAP",
    "MUNICIPIO – SOMENTE CAPEX",
    "BAIRRO – SOMENTE CAPEX",
    "DESCRIÇÃO PI – SOMENTE CAPEX",
    "REGULADO ANEEL",
    "BARRAMENTO/CD. EQUIPAMENTO – SOMENTE OPEX",
    "TIPO INTERVENÇÃO",
    "NÚMERO SI – SOMENTE BLOQUEIO DO ALIMENTADOR (LINHA VIVA) e DESLIGAMENTO PROGRAMADO",
    "INICIO PREVISTO – SOMENTE DESLIGAMENTO PROGRAMADO",
    "FINAL PREVISTO – SOMENTE DESLIGAMENTO PROGRAMADO",
    "SERVIÇOS",
    "OBSERVAÇÃO",
]


class ExportadorErro(ValueError):
    """Erro de validação para entradas do exportador."""


def _carregar_pandas():
    try:
        import pandas as pd
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Dependência ausente: instale pandas e openpyxl para usar o exportador. "
            "Exemplo: pip install pandas openpyxl"
        ) from exc
    return pd


def _normalizar_texto(texto: str) -> str:
    texto = texto.strip().upper()
    texto = texto.replace("–", "-").replace("—", "-")
    texto = re.sub(r"\s+", " ", texto)
    return texto


def carregar_base(caminho: str, sheet_name: str | int | None = 0) -> "pd.DataFrame":
    """Carrega um arquivo Excel e retorna o DataFrame da aba selecionada."""
    pd = _carregar_pandas()

    arquivo = Path(caminho)
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            module=r"openpyxl\.worksheet\._reader",
        )
        return pd.read_excel(arquivo, sheet_name=sheet_name)


def listar_abas(caminho: str) -> list[str]:
    pd = _carregar_pandas()
    arquivo = Path(caminho)
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            module=r"openpyxl\.worksheet\._reader",
        )
        with pd.ExcelFile(arquivo) as excel:
            return list(excel.sheet_names)


def _indice_colunas(df: "pd.DataFrame") -> dict[str, str]:
    indice: dict[str, str] = {}
    for coluna in df.columns:
        chave = _normalizar_texto(str(coluna))
        indice.setdefault(chave, str(coluna))
    return indice


def _resolver_colunas(
    indice_colunas: dict[str, str],
    colunas_desejadas: Iterable[str],
    obrigatorias: bool = True,
) -> tuple[list[str], dict[str, str]]:
    colunas_reais: list[str] = []
    rename_map: dict[str, str] = {}
    faltantes: list[str] = []

    for coluna in colunas_desejadas:
        chave = _normalizar_texto(coluna)
        coluna_real = indice_colunas.get(chave)

        if coluna_real is None:
            if obrigatorias:
                faltantes.append(coluna)
            continue

        if coluna_real not in colunas_reais:
            colunas_reais.append(coluna_real)
            rename_map[coluna_real] = coluna

    if faltantes:
        raise ExportadorErro(
            "As seguintes colunas obrigatórias não existem na base: " + ", ".join(faltantes)
        )

    return colunas_reais, rename_map


def aplicar_filtros(
    df: "pd.DataFrame",
    data_coluna: str,
    data_inicio: str | None,
    data_fim: str | None,
    status_coluna: str,
    status: str | None,
) -> "pd.DataFrame":
    """Aplica filtros de data e status."""
    pd = _carregar_pandas()

    resultado = df.copy()
    indice = _indice_colunas(resultado)

    if data_inicio or data_fim:
        coluna_data = indice.get(_normalizar_texto(data_coluna))
        if not coluna_data:
            raise ExportadorErro(
                f"Coluna de data '{data_coluna}' não encontrada para aplicar filtro de período."
            )

        resultado[coluna_data] = pd.to_datetime(resultado[coluna_data], errors="coerce")

        if data_inicio:
            inicio = pd.to_datetime(data_inicio)
            resultado = resultado[resultado[coluna_data] >= inicio]

        if data_fim:
            fim = pd.to_datetime(data_fim)
            resultado = resultado[resultado[coluna_data] <= fim]

    if status:
        coluna_status = indice.get(_normalizar_texto(status_coluna))
        if not coluna_status:
            raise ExportadorErro(
                f"Coluna de status '{status_coluna}' não encontrada para aplicar filtro de status."
            )

        resultado = resultado[
            resultado[coluna_status].astype(str).str.upper().str.strip() == status.upper().strip()
        ]

    return resultado


def _normalizar_colunas(colunas: str | None) -> list[str]:
    if not colunas:
        return []
    return [col.strip() for col in colunas.split(",") if col.strip()]


def selecionar_colunas(df: "pd.DataFrame", colunas_adicionais: str | None) -> "pd.DataFrame":
    indice = _indice_colunas(df)

    obrigatorias_reais, rename_map = _resolver_colunas(indice, REQUIRED_COLUMNS, obrigatorias=True)

    adicionais = _normalizar_colunas(colunas_adicionais)
    if adicionais:
        extras_reais, _ = _resolver_colunas(indice, adicionais, obrigatorias=False)
        for extra in extras_reais:
            if extra not in obrigatorias_reais:
                obrigatorias_reais.append(extra)

    return df[obrigatorias_reais].rename(columns=rename_map)


def _somente_digitos(valor: str) -> str:
    return re.sub(r"\D+", "", valor)


def _serie_vazia(df: "pd.DataFrame") -> "pd.Series":
    pd = _carregar_pandas()
    return pd.Series([""] * len(df), index=df.index, dtype="object")


def _obter_serie(df: "pd.DataFrame", indice: dict[str, str], nome_coluna: str) -> "pd.Series":
    coluna_real = indice.get(_normalizar_texto(nome_coluna))
    if not coluna_real:
        return _serie_vazia(df)
    return df[coluna_real]


def _normalizar_serie_texto(serie: "pd.Series") -> "pd.Series":
    return serie.where(~serie.isna(), "").astype(str).str.strip()


def transformar_base(
    df: "pd.DataFrame",
    prazo_conclusao: str,
    data_programacao: str,
) -> "pd.DataFrame":
    """Transforma a base de entrada no layout padronizado de exportação."""
    pd = _carregar_pandas()
    indice = _indice_colunas(df)

    capex_opex = _normalizar_serie_texto(_obter_serie(df, indice, "CAPEX/OPEX"))
    status_sap = _normalizar_serie_texto(_obter_serie(df, indice, "STATUS SAP"))

    descricao_obra = _normalizar_serie_texto(_obter_serie(df, indice, "DESCRIÇÃO OBRA"))
    if not descricao_obra.any():
        descricao_obra = _normalizar_serie_texto(_obter_serie(df, indice, "NOME OBRA - SOMENTE CAPEX"))

    data_base = _normalizar_serie_texto(_obter_serie(df, indice, "DATA"))

    equipe = _normalizar_serie_texto(_obter_serie(df, indice, "EQUIPE")).str[-12:]

    elemento_pep = _normalizar_serie_texto(
        _obter_serie(df, indice, "ELEMENTO PEP – SOMENTE CAPEX")
    ).map(_somente_digitos)
    nota_projeto = _normalizar_serie_texto(
        _obter_serie(df, indice, "NOTA PROJETO - SOMENTE CAPEX")
    ).map(_somente_digitos)
    nota_cliente = _normalizar_serie_texto(
        _obter_serie(df, indice, "NOTA CLIENTE - SOMENTE CAPEX")
    ).map(_somente_digitos)

    barramento = _normalizar_serie_texto(
        _obter_serie(df, indice, "BARRAMENTO/CD. EQUIPAMENTO – SOMENTE OPEX")
    )

    ordem_servico = _normalizar_serie_texto(_obter_serie(df, indice, "ORDEM SERVIÇO – SOMENTE OPEX"))
    valor_mo = _normalizar_serie_texto(_obter_serie(df, indice, "VALOR MÃO DE OBRA PROGRAMADA"))
    turno = _normalizar_serie_texto(_obter_serie(df, indice, "TURNO"))
    origem_reclamacao = _normalizar_serie_texto(_obter_serie(df, indice, "ORIGEM RECLAMAÇÃO"))
    referencia = _normalizar_serie_texto(_obter_serie(df, indice, "REFERÊNCIA"))

    mascara_capex = capex_opex.str.upper() == "CAPEX"

    resultado = pd.DataFrame(index=df.index)
    for coluna in REQUIRED_COLUMNS:
        resultado[coluna] = ""

    # Campos diretos / preservados
    resultado["CAPEX/OPEX"] = capex_opex
    resultado["STATUS SAP"] = status_sap
    resultado["NOME OBRA - SOMENTE CAPEX"] = descricao_obra
    resultado["DATA INSPEÇÃO – SOMENTE OPEX"] = data_base

    # Regras CAPEX/OPEX para PEP/notas
    resultado["NOTA PROJETO - SOMENTE CAPEX"] = nota_projeto.where(mascara_capex, "")
    resultado["NOTA CLIENTE - SOMENTE CAPEX"] = nota_cliente.where(mascara_capex, "")
    resultado["ELEMENTO PEP – SOMENTE CAPEX"] = elemento_pep.where(mascara_capex, "")

    # Campos fixos
    resultado["REGIONAL"] = "NORTE"
    resultado["PARCEIRA"] = "SETUP METROPOLITANA (NORTE-EXPANSAO MT/BT)"
    resultado["QUANTIDADES DIAS"] = 1
    resultado["PRAZO CONCLUSÃO"] = prazo_conclusao
    resultado["DATA PROGRAMAÇÃO"] = data_programacao
    resultado["ORÇAMENTO MAT."] = 0
    resultado["TIPO SERVIÇO"] = "EXPANSAO MT"
    resultado["COM RECLAMAÇÃO?"] = "NÃO"
    resultado["TEM RESTRIÇÃO?"] = "NÃO"
    resultado["OBRA VALIDADA EM CAMPO?"] = "SIM"
    resultado["REGULADO ANEEL"] = "SIM"
    resultado["TIPO INTERVENÇÃO"] = "SEM NECESSIDADE DE DESLIGAMENTO"

    # Regras específicas
    resultado["MUNICIPIO – SOMENTE CAPEX"] = ""
    resultado["BAIRRO – SOMENTE CAPEX"] = "URBANO"
    resultado["DESCRIÇÃO PI – SOMENTE CAPEX"] = "DIF"
    resultado["BARRAMENTO/CD. EQUIPAMENTO – SOMENTE OPEX"] = barramento

    # Campos que devem manter valor original
    resultado["EQUIPE"] = equipe
    resultado["ORDEM SERVIÇO – SOMENTE OPEX"] = ordem_servico
    resultado["VALOR MÃO DE OBRA PROGRAMADA"] = valor_mo
    resultado["TURNO"] = turno
    resultado["ORIGEM RECLAMAÇÃO"] = origem_reclamacao
    resultado["REFERÊNCIA"] = referencia

    return resultado


def exportar(df: "pd.DataFrame", saida: str) -> None:
    destino = Path(saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(destino, index=False)

    print(f"Arquivo gerado: {destino}")
    print(f"Total de registros exportados: {len(df)}")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Exportador SIPROG")

    parser.add_argument("--arquivo", help="Caminho do arquivo .xlsx de entrada")
    parser.add_argument("--aba", help="Nome (ou índice) da aba a ser exportada (sobrescreve o padrão PROGRAMACAO_OBRAS)")
    parser.add_argument(
        "--selecionar-aba",
        action="store_true",
        help="Exibe uma lista para selecionar manualmente a aba de trabalho",
    )

    parser.add_argument(
        "--selecionar-arquivos",
        action="store_true",
        help=(
            "Abre uma tela para selecionar a planilha de entrada e a pasta de saída "
            "(útil para execução operacional no Windows)"
        ),
    )
    parser.add_argument(
        "--gui-colunas",
        action="store_true",
        help=(
            "Abre uma interface para pesquisar colunas e visualizar amostras de dados "
            "antes da exportação"
        ),
    )
    parser.add_argument(
        "--gui-execucao",
        action="store_true",
        help="Abre painel visual com logs em tempo real e status/loading da execução",
    )

    parser.add_argument(
        "--data-coluna",
        default=DEFAULT_DATA_COLUMN,
        help=f"Nome da coluna de data (padrão: {DEFAULT_DATA_COLUMN})",
    )
    parser.add_argument("--data-inicio", help="Data inicial no formato YYYY-MM-DD")
    parser.add_argument("--data-fim", help="Data final no formato YYYY-MM-DD")

    parser.add_argument(
        "--status-coluna",
        default=DEFAULT_STATUS_COLUMN,
        help=f"Nome da coluna de status (padrão: {DEFAULT_STATUS_COLUMN})",
    )
    parser.add_argument("--status", help="Valor do status para filtro")

    parser.add_argument(
        "--colunas",
        help=(
            "Colunas adicionais separadas por vírgula para incluir no final do layout padrão "
            "(as colunas obrigatórias do SIPROG sempre serão exportadas)"
        ),
    )
    parser.add_argument("--saida", default=DEFAULT_OUTPUT, help="Arquivo de saída .xlsx")
    parser.add_argument("--prazo-conclusao", help="Data para preencher PRAZO CONCLUSÃO")
    parser.add_argument("--data-programacao", help="Data para preencher DATA PROGRAMAÇÃO")

    return parser


def _parse_sheet_name(sheet_name: str | None) -> str | int | None:
    if sheet_name is None:
        return None
    return int(sheet_name) if sheet_name.isdigit() else sheet_name


def _selecionar_arquivo_e_pasta(saida_padrao: str) -> tuple[str, str]:
    raiz = Tk()
    raiz.withdraw()
    raiz.attributes("-topmost", True)

    arquivo = filedialog.askopenfilename(
        title="Selecione a planilha de entrada",
        filetypes=[("Planilhas Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")],
    )
    if not arquivo:
        raise ExportadorErro("Seleção cancelada: nenhuma planilha foi escolhida.")

    pasta = filedialog.askdirectory(title="Selecione a pasta de trabalho (saída)")
    if not pasta:
        raise ExportadorErro("Seleção cancelada: nenhuma pasta de trabalho foi escolhida.")

    raiz.destroy()

    saida = Path(pasta) / Path(saida_padrao).name
    return arquivo, str(saida)


def _escolher_aba_interativamente(caminho_arquivo: str) -> str | int:
    abas = listar_abas(caminho_arquivo)
    if not abas:
        raise ExportadorErro("Nenhuma aba encontrada no arquivo selecionado.")

    if len(abas) == 1:
        print(f"Apenas uma aba encontrada. Usando automaticamente: {abas[0]}")
        return abas[0]

    print("Abas disponíveis no arquivo:")
    for i, aba in enumerate(abas, start=1):
        print(f"  {i}) {aba}")

    while True:
        escolha = input("Selecione o número da aba desejada: ").strip()
        if escolha.isdigit():
            indice = int(escolha)
            if 1 <= indice <= len(abas):
                return abas[indice - 1]
        print("Opção inválida. Informe um número da lista.")


def _abrir_gui_colunas(df: "pd.DataFrame") -> list[str]:
    try:
        raiz = Tk()
        raiz.withdraw()
    except Exception as exc:  # pragma: no cover - depende de ambiente gráfico
        raise ExportadorErro(
            "Não foi possível abrir a interface gráfica de colunas neste ambiente. "
            "Use --colunas manualmente."
        ) from exc

    janela = Toplevel(raiz)
    janela.title("Visualização de Colunas - Exportador SIPROG")
    janela.geometry("980x620")

    ttk.Label(janela, text="Pesquisar coluna:").pack(anchor="w", padx=12, pady=(10, 2))

    filtro_var = StringVar(value="")
    entrada = ttk.Entry(janela, textvariable=filtro_var)
    entrada.pack(fill="x", padx=12)

    frame_lista = ttk.Frame(janela)
    frame_lista.pack(fill="both", expand=True, padx=12, pady=10)

    lista = ttk.Treeview(frame_lista, columns=("coluna", "amostra"), show="headings", height=16)
    lista.heading("coluna", text="Coluna")
    lista.heading("amostra", text="Amostra (até 3 valores não vazios)")
    lista.column("coluna", width=340, anchor="w")
    lista.column("amostra", width=600, anchor="w")

    scroll = ttk.Scrollbar(frame_lista, orient="vertical", command=lista.yview)
    lista.configure(yscrollcommand=scroll.set)

    lista.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    selecionadas: list[str] = []

    colunas = [str(c) for c in df.columns]

    def amostra_coluna(col: str) -> str:
        serie = df[col].dropna().astype(str)
        vals = []
        for v in serie:
            v = v.strip()
            if not v:
                continue
            if v not in vals:
                vals.append(v)
            if len(vals) == 3:
                break
        return " | ".join(vals) if vals else "(sem valores não vazios)"

    cache = {c: amostra_coluna(c) for c in colunas}

    def preencher() -> None:
        termo = filtro_var.get().strip().lower()
        for iid in lista.get_children():
            lista.delete(iid)
        for c in colunas:
            if termo and termo not in c.lower() and termo not in cache[c].lower():
                continue
            lista.insert("", END, values=(c, cache[c]))

    def confirmar() -> None:
        nonlocal selecionadas
        selecionadas = [lista.item(iid, "values")[0] for iid in lista.selection()]
        janela.destroy()

    botoes = ttk.Frame(janela)
    botoes.pack(fill="x", padx=12, pady=(0, 12))

    ttk.Button(botoes, text="Usar colunas selecionadas", command=confirmar).pack(side="left")
    ttk.Button(botoes, text="Continuar sem selecionar", command=janela.destroy).pack(side="left", padx=8)

    filtro_var.trace_add("write", lambda *_: preencher())
    preencher()
    entrada.focus_set()

    janela.transient(raiz)
    janela.grab_set()
    janela.protocol("WM_DELETE_WINDOW", janela.destroy)
    raiz.wait_window(janela)
    raiz.destroy()

    return selecionadas


def _escolher_aba_gui(caminho_arquivo: str) -> str:
    abas = listar_abas(caminho_arquivo)
    if not abas:
        raise ExportadorErro("Nenhuma aba encontrada no arquivo selecionado.")
    if len(abas) == 1:
        return abas[0]

    raiz = Tk()
    raiz.withdraw()
    janela = Toplevel(raiz)
    janela.title("Selecionar aba")
    janela.geometry("460x420")

    ttk.Label(janela, text="Selecione a aba para processar:").pack(anchor="w", padx=12, pady=(12, 6))
    lista = ttk.Treeview(janela, columns=("aba",), show="headings", height=14)
    lista.heading("aba", text="Aba")
    lista.column("aba", width=420, anchor="w")
    lista.pack(fill="both", expand=True, padx=12)

    for aba in abas:
        lista.insert("", END, values=(aba,))

    selecionada: str = abas[0]

    def confirmar() -> None:
        nonlocal selecionada
        itens = lista.selection()
        if itens:
            selecionada = str(lista.item(itens[0], "values")[0])
        janela.destroy()

    ttk.Button(janela, text="Confirmar", command=confirmar).pack(pady=10)
    janela.transient(raiz)
    janela.grab_set()
    janela.protocol("WM_DELETE_WINDOW", confirmar)
    raiz.wait_window(janela)
    raiz.destroy()
    return selecionada




def _listar_abas_texto(abas: list[str]) -> str:
    if not abas:
        return "(nenhuma aba)"
    return ", ".join(abas)

def _executar_fluxo(args: argparse.Namespace, log=None, progresso=None) -> None:
    def _log(msg: str) -> None:
        if log:
            log(msg)
        else:
            print(msg)

    if progresso:
        progresso(5, "Iniciando")

    if args.selecionar_arquivos:
        _log("Abrindo seleção de planilha e pasta...")
        args.arquivo, args.saida = _selecionar_arquivo_e_pasta(args.saida)

    _log("Verificando abas disponíveis na planilha...")
    abas = listar_abas(args.arquivo)
    _log(f"Abas encontradas ({len(abas)}): {_listar_abas_texto(abas)}")

    sheet_name = _parse_sheet_name(args.aba)
    if sheet_name is None:
        nomes_normalizados = {_normalizar_texto(a): a for a in abas}
        sheet_name = nomes_normalizados.get(_normalizar_texto(DEFAULT_WORKSHEET), DEFAULT_WORKSHEET)
        if _normalizar_texto(DEFAULT_WORKSHEET) in nomes_normalizados:
            _log(f"Aba padrão aplicada: {sheet_name}")
        else:
            _log(
                f"Aba padrão '{DEFAULT_WORKSHEET}' não encontrada pelo nome exato. Tentando carregar mesmo assim."
            )
    else:
        _log(f"Aba informada manualmente: {sheet_name}")

    _log(f"Aba selecionada para carga: {sheet_name}")
    _log(f"Carregando base: {args.arquivo}")
    if progresso:
        progresso(20, "Carregando base")
    df = carregar_base(args.arquivo, sheet_name=sheet_name)
    _log(f"Registros carregados: {len(df)}")

    if args.gui_colunas and not args.gui_execucao:
        _log("Abrindo visualização de colunas...")
        colunas_gui = _abrir_gui_colunas(df)
        if colunas_gui:
            adicionais_gui = ",".join(colunas_gui)
            args.colunas = f"{args.colunas},{adicionais_gui}" if args.colunas else adicionais_gui
            _log(f"Colunas adicionais selecionadas: {len(colunas_gui)}")
    elif args.gui_colunas and args.gui_execucao:
        _log("Aviso: --gui-colunas é ignorado com --gui-execucao para evitar travamentos de interface.")

    if progresso:
        progresso(40, "Aplicando filtros")
    _log("Aplicando filtros...")
    df = aplicar_filtros(
        df,
        data_coluna=args.data_coluna,
        data_inicio=args.data_inicio,
        data_fim=args.data_fim,
        status_coluna=args.status_coluna,
        status=args.status,
    )
    _log(f"Registros após filtros: {len(df)}")

    if progresso:
        progresso(65, "Transformando dados")
    _log("Aplicando regras de transformação...")
    df = transformar_base(
        df,
        prazo_conclusao=args.prazo_conclusao,
        data_programacao=args.data_programacao,
    )

    if progresso:
        progresso(82, "Montando layout")
    _log("Montando layout final...")
    df = selecionar_colunas(df, args.colunas)

    if progresso:
        progresso(95, "Exportando")
    destino_final = str(Path(args.saida).resolve())
    _log(f"Exportando arquivo: {destino_final}")
    exportar(df, args.saida)
    _log(f"Arquivo XLSX salvo em: {destino_final}")

    if progresso:
        progresso(100, "Concluído")
    _log("Processo finalizado com sucesso.")


def _executar_com_gui(args: argparse.Namespace) -> None:
    fila: Queue[tuple[str, str]] = Queue()

    raiz = Tk()
    raiz.title("Exportador SIPROG - Execução")
    raiz.geometry("900x560")

    status_var = StringVar(value="Preparando execução...")
    progresso = ttk.Progressbar(raiz, orient="horizontal", mode="determinate", maximum=100)
    progresso.pack(fill="x", padx=12, pady=(12, 6))
    ttk.Label(raiz, textvariable=status_var).pack(anchor="w", padx=12)

    logs = ScrolledText(raiz, height=24, state="disabled")
    logs.pack(fill="both", expand=True, padx=12, pady=12)

    def log_local(msg: str) -> None:
        logs.configure(state="normal")
        logs.insert(END, msg + "\n")
        logs.see(END)
        logs.configure(state="disabled")
        raiz.update_idletasks()

    # Pré-etapas no thread principal para evitar travamentos de GUI.
    if args.selecionar_arquivos:
        status_var.set("Selecionando arquivo e pasta...")
        raiz.update_idletasks()
        args.arquivo, args.saida = _selecionar_arquivo_e_pasta(args.saida)
        log_local(f"Arquivo selecionado: {args.arquivo}")
        log_local(f"Saída configurada: {Path(args.saida).resolve()}")

    status_var.set("Verificando abas...")
    raiz.update_idletasks()
    abas = listar_abas(args.arquivo)
    log_local(f"Abas detectadas ({len(abas)}): {_listar_abas_texto(abas)}")

    if args.selecionar_aba:
        log_local("Aviso: --selecionar-aba foi ignorado. O fluxo está fixado na aba PROGRAMACAO_OBRAS.")

    def add_log(msg: str) -> None:
        fila.put(("log", msg))

    def set_progress(valor: int, status: str) -> None:
        fila.put(("progress", f"{valor}|{status}"))

    def worker() -> None:
        try:
            _executar_fluxo(args, log=add_log, progresso=set_progress)
            fila.put(("done", "ok"))
        except Exception:
            fila.put(("log", traceback.format_exc()))
            fila.put(("done", "erro"))

    def processar_fila() -> None:
        try:
            while True:
                tipo, conteudo = fila.get_nowait()
                if tipo == "log":
                    log_local(conteudo)
                elif tipo == "progress":
                    valor_txt, status = conteudo.split("|", 1)
                    progresso["value"] = int(valor_txt)
                    status_var.set(status)
                elif tipo == "done":
                    if conteudo == "ok":
                        status_var.set("Concluído com sucesso")
                    else:
                        status_var.set("Erro durante execução (veja logs)")
                    return
        except Empty:
            pass
        raiz.after(120, processar_fila)

    threading.Thread(target=worker, daemon=True).start()
    processar_fila()
    raiz.mainloop()


def _validar_argumentos(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if not args.arquivo and not args.selecionar_arquivos:
        parser.error("informe --arquivo ou use --selecionar-arquivos para abrir a tela de seleção")
    if not args.prazo_conclusao:
        parser.error("informe --prazo-conclusao")
    if not args.data_programacao:
        parser.error("informe --data-programacao")


def main() -> None:
    parser = construir_parser()
    args = parser.parse_args()
    _validar_argumentos(args, parser)

    if args.gui_execucao:
        try:
            _executar_com_gui(args)
            return
        except TclError:
            print("Aviso: interface gráfica indisponível neste ambiente. Executando em modo terminal.")

    _executar_fluxo(args)


if __name__ == "__main__":
    main()
