from pathlib import Path

import csv
import pytest

from src.material_storage import Material
from src.orcamento_obra import (
    COLUNAS_EXPORTACAO,
    ItemSelecionado,
    calcular_metragem_final,
    calcular_orcamento,
    exportar_csv_padrao,
)


def test_metragem_minima_com_sangria():
    assert calcular_metragem_final(1, 10) == 31.5


def test_lancamento_converte_para_km():
    res = calcular_orcamento(
        supervisor="S",
        equipe="E",
        descricao_obra="D",
        encarregado="N",
        tipo_servico="Lançamento de Cabo Elétrico",
        servico="Lançamento Aéreo",
        cod_servico="CAB.001",
        valor_unitario_servico=1850.0,
        quantidade_clientes=5,
        metros_ramal=40,
        distancia_km=2.0,
        itens_materiais=[ItemSelecionado(Material("M1", "Cabo", "M", 10.0), 100)],
    )
    assert res.quantidade_servico == pytest.approx(0.21)
    assert res.valor_transporte == pytest.approx(24.0)


def test_tipo_servico_obrigatorio():
    with pytest.raises(ValueError):
        calcular_orcamento(
            supervisor="S",
            equipe="E",
            descricao_obra="D",
            encarregado="N",
            tipo_servico="",
            servico="X",
            cod_servico="COD",
            valor_unitario_servico=10.0,
            quantidade_clientes=1,
            metros_ramal=30,
            distancia_km=0,
            itens_materiais=[],
        )


def test_exporta_csv_padrao_com_campos_vazios_e_valores_consistentes(tmp_path: Path):
    res = calcular_orcamento(
        supervisor="Sup",
        equipe="Eq",
        descricao_obra="Obra",
        encarregado="Enc",
        tipo_servico="Obra Elétrica",
        servico="Instalação de Poste",
        cod_servico="OBR.001",
        valor_unitario_servico=52.0,
        quantidade_clientes=2,
        metros_ramal=30,
        distancia_km=1.5,
        itens_materiais=[
            ItemSelecionado(Material("M1", "Poste", "UN", 100.0, "OBR.001", "SIM.1"), 2),
            ItemSelecionado(Material("M2", "Cabo", "M", 10.0, "CAB.1", "SIM.2"), 5),
        ],
    )

    out = tmp_path / "padrao.csv"
    exportar_csv_padrao(res, out)

    with out.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        assert reader.fieldnames == COLUNAS_EXPORTACAO

    assert len(rows) == 2
    assert rows[0]["CHAVE"] == ""
    assert rows[0]["DATA"] == ""
    assert rows[0]["PEP"] == ""
    assert rows[0]["VALOR_UNITÁRIO"] == "100.00"
    assert rows[0]["QTD_REALIZADO"] == "2.0000"
    assert rows[0]["VALOR_REALIZADO"] == "200.00"
    assert rows[0]["CALC. TRANSPORTE"] == "9.00"
    assert rows[0]["VALOR_TOTAL"] == "209.00"
    assert rows[0]["DIFERENÇA"] == "9.00"
