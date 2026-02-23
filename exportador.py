#!/usr/bin/env python3
"""Exportador de planilhas para ingestão no SIPROG."""

from __future__ import annotations

import argparse
import re
import sys
import threading
import traceback
import unicodedata
import warnings
from pathlib import Path
from queue import Empty, Queue
from typing import TYPE_CHECKING

from tkinter import END, StringVar, TclError, Tk, filedialog, ttk
from tkinter.scrolledtext import ScrolledText

if TYPE_CHECKING:
    import pandas as pd

DEFAULT_OUTPUT = "exportacao_siprog.xlsx"
DEFAULT_DATA_COLUMN = "DATA"
DEFAULT_STATUS_COLUMN = "STATUS"
DEFAULT_WORKSHEET = "PROGRAMAÇÃO_OBRAS"

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

ESSENTIAL_COLUMNS = ["DATA", "DESCRIÇÃO OBRA", "STATUS", "EQUIPE", "PEP"]
STRICT_SOURCE_COLUMNS = ["DATA", "DESCRIÇÃO OBRA", "STATUS", "EQUIPE", "PEP"]


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


def normalizar(texto: str) -> str:
    return (
        unicodedata.normalize("NFKD", str(texto))
        .encode("ASCII", "ignore")
        .decode("ASCII")
        .upper()
        .strip()
    )


def encontrar_aba(sheet_names: list[str], nome_desejado: str) -> str | None:
    alvo = normalizar(nome_desejado)
    for aba in sheet_names:
        if normalizar(aba) == alvo:
            return aba
    return None


def _normalizar_texto(texto: str) -> str:
    return re.sub(r"\s+", " ", str(texto).strip()).upper()


def carregar_base(arquivo: str, nome_aba: str) -> "pd.DataFrame":
    pd = _carregar_pandas()
    caminho = Path(arquivo)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module=r"openpyxl\.worksheet\._reader")
        excel = pd.ExcelFile(caminho)
        aba_real = encontrar_aba(list(excel.sheet_names), nome_aba)
        if not aba_real:
            raise ExportadorErro(f"Aba '{nome_aba}' não encontrada. Abas: {', '.join(excel.sheet_names)}")
        df = pd.read_excel(caminho, sheet_name=aba_real)

    if isinstance(df, dict):
        df = list(df.values())[0]

    df.columns = [str(c).strip() for c in df.columns]
    return df.fillna("")


def _indice_colunas(df: "pd.DataFrame") -> dict[str, str]:
    return {_normalizar_texto(c): str(c) for c in df.columns}


def _serie_vazia(df: "pd.DataFrame") -> "pd.Series":
    pd = _carregar_pandas()
    return pd.Series([""] * len(df), index=df.index, dtype="object")





def _obter_serie_obrigatoria(df: "pd.DataFrame", indice: dict[str, str], nome_coluna: str) -> "pd.Series":
    coluna_real = indice.get(_normalizar_texto(nome_coluna))
    if not coluna_real:
        raise ExportadorErro(
            f"Coluna obrigatória '{nome_coluna}' ausente na base. "
            "Sem essa coluna o sistema não pode processar sem simular dados."
        )
    return df[coluna_real]

def _obter_serie(df: "pd.DataFrame", indice: dict[str, str], nome_coluna: str) -> "pd.Series":
    coluna_real = indice.get(_normalizar_texto(nome_coluna))
    if not coluna_real:
        return _serie_vazia(df)
    return df.get(coluna_real, _serie_vazia(df))


def _texto(serie: "pd.Series") -> "pd.Series":
    return serie.where(~serie.isna(), "").astype(str).str.strip()


def _somente_digitos(valor: str) -> str:
    return re.sub(r"\D+", "", valor)


def validar_colunas_essenciais(df: "pd.DataFrame") -> None:
    indice = _indice_colunas(df)
    faltantes = [c for c in STRICT_SOURCE_COLUMNS if _normalizar_texto(c) not in indice]
    if faltantes:
        raise ExportadorErro(
            "Colunas essenciais ausentes para transformação (sem simulação de dados): " + ", ".join(faltantes)
        )




def _parse_data_param(valor: str, nome_parametro: str):
    pd = _carregar_pandas()
    texto = str(valor).strip()
    if not texto:
        raise ExportadorErro(f"Parâmetro {nome_parametro} vazio.")

    for dayfirst in (False, True):
        try:
            return pd.to_datetime(texto, errors="raise", dayfirst=dayfirst)
        except (TypeError, ValueError):
            continue

    raise ExportadorErro(
        f"Data inválida em {nome_parametro}: '{valor}'. Use YYYY-MM-DD ou DD/MM/YYYY."
    )


def aplicar_filtros(
    df: "pd.DataFrame",
    data_coluna: str,
    data_inicio: str | None,
    data_fim: str | None,
    status_coluna: str,
    status: str | None,
) -> "pd.DataFrame":
    pd = _carregar_pandas()
    resultado = df.copy()
    indice = _indice_colunas(resultado)

    if data_inicio or data_fim:
        col_data = indice.get(_normalizar_texto(data_coluna))
        if not col_data:
            # fallback resiliente para bases que usam DATA em vez de DATA PROGRAMAÇÃO
            col_data = indice.get(_normalizar_texto("DATA"))
        if not col_data:
            disponiveis = ", ".join(list(resultado.columns)[:12])
            raise ExportadorErro(
                f"Coluna de data '{data_coluna}' não encontrada. "
                f"Informe --data-coluna corretamente. Exemplo de colunas disponíveis: {disponiveis}"
            )
        serie_data_filtro = pd.to_datetime(resultado[col_data], errors="coerce")
        data_inicio_dt = _parse_data_param(data_inicio, "--data-inicio") if data_inicio else None
        data_fim_dt = _parse_data_param(data_fim, "--data-fim") if data_fim else None

        if data_inicio_dt is not None:
            resultado = resultado[serie_data_filtro >= data_inicio_dt]
            serie_data_filtro = serie_data_filtro.loc[resultado.index]
        if data_fim_dt is not None:
            resultado = resultado[serie_data_filtro <= data_fim_dt]

    if status:
        col_status = indice.get(_normalizar_texto(status_coluna))
        if not col_status:
            raise ExportadorErro(f"Coluna de status '{status_coluna}' não encontrada.")
        resultado = resultado[
            resultado[col_status].astype(str).str.upper().str.strip() == status.upper().strip()
        ]

    return resultado


def transformar_base(df: "pd.DataFrame", prazo_conclusao: str) -> "pd.DataFrame":
    pd = _carregar_pandas()
    validar_colunas_essenciais(df)
    indice = _indice_colunas(df)

    data_base = _texto(_obter_serie_obrigatoria(df, indice, "DATA"))
    descricao_obra = _texto(_obter_serie_obrigatoria(df, indice, "DESCRIÇÃO OBRA"))
    status_sap = _texto(_obter_serie_obrigatoria(df, indice, "STATUS"))
    equipe = _texto(_obter_serie_obrigatoria(df, indice, "EQUIPE")).str[-12:]
    pep_original = _texto(_obter_serie_obrigatoria(df, indice, "PEP"))

    mask_pep_valido = pep_original.str.strip() != ""
    df = df.loc[mask_pep_valido].copy()
    pep_original = pep_original.loc[df.index]

    retorno = _texto(_obter_serie(df, indice, "RETORNO"))
    df = df.loc[retorno.str.strip() == ""].copy()
    pep_original = pep_original.loc[df.index]

    indice = _indice_colunas(df)
    data_base = _texto(_obter_serie_obrigatoria(df, indice, "DATA"))
    descricao_obra = _texto(_obter_serie_obrigatoria(df, indice, "DESCRIÇÃO OBRA"))
    status_sap = _texto(_obter_serie_obrigatoria(df, indice, "STATUS"))
    equipe = _texto(_obter_serie_obrigatoria(df, indice, "EQUIPE")).str[-12:]

    valor_mo = _texto(_obter_serie(df, indice, "VALOR_PROGRAMADO"))
    turno = _texto(_obter_serie(df, indice, "TURNO"))
    if _normalizar_texto("REFERENCIA") in indice:
        referencia = _obter_serie(df, indice, "REFERENCIA")
    else:
        referencia = _obter_serie(df, indice, "REFERÊNCIA")
    referencia = referencia.where(~referencia.isna(), pd.NA)

    municipio = _texto(_obter_serie(df, indice, "MUNICIPIO"))
    barramento = _texto(_obter_serie(df, indice, "BARRAMENTO/CD. EQUIPAMENTO – SOMENTE OPEX"))

    linhas_validas = (data_base != "") | (descricao_obra != "") | (status_sap != "") | (equipe != "") | (pep_original != "")
    df_base = df.loc[linhas_validas].copy()

    resultado = pd.DataFrame(index=df_base.index)
    for col in REQUIRED_COLUMNS:
        resultado[col] = ""

    # Diretos
    resultado["CAPEX/OPEX"] = "CAPEX"
    resultado["DATA INSPEÇÃO – SOMENTE OPEX"] = data_base.loc[df_base.index]
    resultado["NOME OBRA - SOMENTE CAPEX"] = descricao_obra.loc[df_base.index]
    resultado["STATUS SAP"] = status_sap.loc[df_base.index]
    resultado["EQUIPE"] = equipe.loc[df_base.index]

    # PEP/Notas somente CAPEX
    pep_valid = pep_original.loc[df_base.index]
    resultado["NOTA PROJETO - SOMENTE CAPEX"] = pep_valid
    resultado["NOTA CLIENTE - SOMENTE CAPEX"] = pep_valid
    resultado["ELEMENTO PEP – SOMENTE CAPEX"] = pep_valid

    # Fixos
    resultado["REGIONAL"] = "NORTE"
    resultado["PARCEIRA"] = "SETUP METROPOLITANA (NORTE-EXPANSAO MT/BT)"
    resultado["QUANTIDADES DIAS"] = 1
    resultado["PRAZO CONCLUSÃO"] = prazo_conclusao
    resultado["DATA PROGRAMAÇÃO"] = data_base.loc[df_base.index]
    resultado["ORÇAMENTO MAT."] = 0
    resultado["TIPO SERVIÇO"] = "EXPANSAO MT"
    resultado["COM RECLAMAÇÃO?"] = "NÃO"
    resultado["TEM RESTRIÇÃO?"] = "NÃO"
    resultado["OBRA VALIDADA EM CAMPO?"] = "SIM"
    resultado["BAIRRO – SOMENTE CAPEX"] = "URBANO"
    resultado["DESCRIÇÃO PI – SOMENTE CAPEX"] = "DIF"
    resultado["REGULADO ANEEL"] = "SIM"
    resultado["TIPO INTERVENÇÃO"] = "SEM NECESSIDADE DE DESLIGAMENTO"

    # Campos opcionais / vazios preservados
    resultado["REFERÊNCIA"] = referencia.loc[df_base.index]
    resultado["MUNICIPIO – SOMENTE CAPEX"] = municipio.loc[df_base.index]
    resultado["ORDEM SERVIÇO – SOMENTE OPEX"] = ""
    resultado["VALOR MÃO DE OBRA PROGRAMADA"] = valor_mo.loc[df_base.index]
    resultado["TURNO"] = turno.loc[df_base.index]
    resultado["ORIGEM RECLAMAÇÃO"] = ""
    resultado["BARRAMENTO/CD. EQUIPAMENTO – SOMENTE OPEX"] = barramento.loc[df_base.index]

    return resultado


def exportar(df: "pd.DataFrame", saida: str) -> str:
    destino = Path(saida).resolve()
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(destino, index=False)
    return str(destino)


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
    return arquivo, str(Path(pasta) / Path(saida_padrao).name)


def _selecionar_datas_gui(args: argparse.Namespace) -> None:
    """Seleciona datas de programação/conclusão e filtros opcionais em janela."""
    janela = Tk()
    janela.title("Selecionar datas da exportação")
    janela.geometry("520x290")

    campos = [
        ("Prazo Conclusão*", "prazo_conclusao", args.prazo_conclusao or ""),
        ("Data Início (filtro opcional)", "data_inicio", args.data_inicio or ""),
        ("Data Fim (filtro opcional)", "data_fim", args.data_fim or ""),
    ]

    entradas: dict[str, ttk.Entry] = {}
    for i, (label, chave, valor) in enumerate(campos):
        ttk.Label(janela, text=f"{label} (YYYY-MM-DD ou DD/MM/YYYY)").grid(row=i, column=0, sticky="w", padx=12, pady=(10 if i == 0 else 6, 0))
        e = ttk.Entry(janela, width=34)
        e.grid(row=i, column=1, padx=12, pady=(10 if i == 0 else 6, 0))
        e.insert(0, valor)
        entradas[chave] = e

    confirmado = {"ok": False}

    def confirmar() -> None:
        args.prazo_conclusao = entradas["prazo_conclusao"].get().strip()
        args.data_inicio = entradas["data_inicio"].get().strip() or None
        args.data_fim = entradas["data_fim"].get().strip() or None
        if not args.prazo_conclusao:
            from tkinter import messagebox
            messagebox.showerror("Datas obrigatórias", "Preencha Prazo Conclusão.")
            return
        confirmado["ok"] = True
        janela.destroy()

    ttk.Button(janela, text="Confirmar", command=confirmar).grid(row=6, column=0, padx=12, pady=16, sticky="w")
    ttk.Button(janela, text="Cancelar", command=janela.destroy).grid(row=6, column=1, padx=12, pady=16, sticky="e")

    janela.mainloop()

    if not confirmado["ok"]:
        raise ExportadorErro("Seleção de datas cancelada pelo usuário.")


def executar_pipeline(args: argparse.Namespace, log=print, progresso=None) -> None:
    if args.selecionar_arquivos:
        log("Abrindo seleção de planilha e pasta...")
        try:
            args.arquivo, args.saida = _selecionar_arquivo_e_pasta(args.saida)
        except TclError as exc:
            raise ExportadorErro(
                "Não foi possível abrir a seleção de arquivo/pasta neste ambiente. "
                "Informe --arquivo e --saida manualmente."
            ) from exc

    if args.selecionar_datas:
        log("Abrindo seleção de datas...")
        try:
            _selecionar_datas_gui(args)
        except TclError as exc:
            raise ExportadorErro(
                "Não foi possível abrir a seleção visual de datas neste ambiente. "
                "Informe --prazo-conclusao manualmente."
            ) from exc

    if progresso:
        progresso(10, "Carregando planilha")
    log(f"Carregando aba alvo: {DEFAULT_WORKSHEET}")
    df = carregar_base(args.arquivo, DEFAULT_WORKSHEET if not args.aba else args.aba)
    log(f"Registros carregados: {len(df)}")

    if progresso:
        progresso(35, "Aplicando filtros")
    df = aplicar_filtros(
        df,
        data_coluna=args.data_coluna,
        data_inicio=args.data_inicio,
        data_fim=args.data_fim,
        status_coluna=args.status_coluna,
        status=args.status,
    )
    log(f"Registros após filtros: {len(df)}")

    if progresso:
        progresso(65, "Transformando")
    df_final = transformar_base(df, args.prazo_conclusao)

    if progresso:
        progresso(90, "Exportando")
    caminho = exportar(df_final, args.saida)
    log(f"Arquivo XLSX salvo em: {caminho}")

    if progresso:
        progresso(100, "Concluído")


def executar_gui(args: argparse.Namespace) -> None:
    fila: Queue[tuple[str, str]] = Queue()

    raiz = Tk()
    raiz.title("Exportador SIPROG - Execução")
    raiz.geometry("900x560")

    status_var = StringVar(value="Pronto para importar")
    bar = ttk.Progressbar(raiz, orient="horizontal", mode="determinate", maximum=100)
    bar.pack(fill="x", padx=12, pady=(12, 6))
    ttk.Label(raiz, textvariable=status_var).pack(anchor="w", padx=12)

    frame_botoes = ttk.Frame(raiz)
    frame_botoes.pack(fill="x", padx=12, pady=(0, 8))
    btn_importar = ttk.Button(frame_botoes, text="Importar novamente")
    btn_importar.pack(side="left")

    logs = ScrolledText(raiz, height=24, state="disabled")
    logs.pack(fill="both", expand=True, padx=12, pady=12)

    em_execucao = {"valor": False}

    def log_local(msg: str) -> None:
        logs.configure(state="normal")
        logs.insert(END, msg + "\n")
        logs.see(END)
        logs.configure(state="disabled")
        raiz.update_idletasks()

    def log_worker(msg: str) -> None:
        fila.put(("log", msg))

    def progresso(valor: int, msg: str) -> None:
        fila.put(("progress", f"{valor}|{msg}"))

    def habilitar_importar() -> None:
        btn_importar.config(state="normal")
        em_execucao["valor"] = False

    def desabilitar_importar() -> None:
        btn_importar.config(state="disabled")
        em_execucao["valor"] = True

    def worker() -> None:
        try:
            executar_pipeline(args, log=log_worker, progresso=progresso)
            fila.put(("done", "ok"))
        except Exception:
            fila.put(("log", traceback.format_exc()))
            fila.put(("done", "erro"))
        finally:
            raiz.after(0, habilitar_importar)

    def iniciar_importacao() -> None:
        if em_execucao["valor"]:
            return
        desabilitar_importar()
        bar["value"] = 0
        status_var.set("Iniciando importação...")
        threading.Thread(target=worker, daemon=True).start()

    def pump() -> None:
        try:
            while True:
                tipo, conteudo = fila.get_nowait()
                if tipo == "log":
                    log_local(conteudo)
                elif tipo == "progress":
                    v, msg = conteudo.split("|", 1)
                    bar["value"] = int(v)
                    status_var.set(msg)
                elif tipo == "done":
                    status_var.set("Concluído com sucesso" if conteudo == "ok" else "Erro (veja logs)")
        except Empty:
            pass
        raiz.after(120, pump)

    btn_importar.config(command=iniciar_importacao)
    pump()
    iniciar_importacao()
    raiz.mainloop()


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Exportador SIPROG")
    parser.add_argument("--arquivo", help="Caminho do arquivo .xlsx de entrada")
    parser.add_argument(
        "--aba",
        help=(
            "Nome (ou índice) da aba a ser exportada. Se omitido, usa PROGRAMAÇÃO_OBRAS "
            "com normalização resiliente"
        ),
    )
    parser.add_argument("--selecionar-arquivos", action="store_true", help="Seleciona arquivo/pasta via janela")
    parser.add_argument("--gui-execucao", action="store_true", help="Executa com painel de logs e progresso")
    parser.add_argument("--selecionar-datas", action="store_true", help="Abre janela para selecionar datas obrigatórias e filtros opcionais")

    parser.add_argument("--data-coluna", default=DEFAULT_DATA_COLUMN)
    parser.add_argument("--data-inicio")
    parser.add_argument("--data-fim")
    parser.add_argument("--status-coluna", default=DEFAULT_STATUS_COLUMN)
    parser.add_argument("--status")

    parser.add_argument("--saida", default=DEFAULT_OUTPUT)
    parser.add_argument("--prazo-conclusao", help="Data para preencher PRAZO CONCLUSÃO")
    return parser



def _aplicar_modo_autonomo_se_sem_args(args: argparse.Namespace) -> None:
    """Quando executado sem argumentos (ex.: duplo clique no .exe), habilita modo gui autônomo."""
    if len(sys.argv) != 1:
        return

    args.selecionar_arquivos = True
    args.selecionar_datas = True
    args.gui_execucao = True
def validar_argumentos(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if not args.arquivo and not args.selecionar_arquivos:
        parser.error("informe --arquivo ou use --selecionar-arquivos (no .exe, execute sem argumentos para abrir as telas)")
    if not args.selecionar_datas:
        if not args.prazo_conclusao:
            parser.error("informe --prazo-conclusao ou use --selecionar-datas")


def main() -> None:
    parser = construir_parser()
    args = parser.parse_args()
    _aplicar_modo_autonomo_se_sem_args(args)
    validar_argumentos(args, parser)

    if args.gui_execucao:
        try:
            executar_gui(args)
            return
        except TclError:
            print("Aviso: GUI indisponível neste ambiente. Executando em modo terminal.")

    executar_pipeline(args)


if __name__ == "__main__":
    main()
