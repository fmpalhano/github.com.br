from pathlib import Path

import pytest

from src.base_materiais import MaterialBase
from src.orcamento_obra import (
    ItemSelecionado,
    calcular_metragem_final,
    calcular_orcamento,
    exportar_orcamento_csv,
    formatar_moeda,
)


def test_calcular_metragem_final_com_minimo_e_sangria():
    assert calcular_metragem_final(1, 10) == 31.5
    assert calcular_metragem_final(3, 20) == 63.0


def test_calculo_financeiro_lancamento_de_cabo():
    material = MaterialBase("COD1", "CABO TESTE", "M", 10.0)
    itens = [ItemSelecionado(material=material, quantidade=50)]

    resultado = calcular_orcamento(
        tipo_servico="Lançamento de Cabo",
        quantidade_clientes=5,
        metros_ramal=40,
        distancia=100,
        itens_materiais=itens,
    )

    assert resultado.metragem_final == 210.0
    assert resultado.quantidade_servico == 0.21
    assert resultado.valor_servico == pytest.approx(388.5)
    assert resultado.valor_materiais == 500.0
    assert resultado.valor_total == pytest.approx(888.5)


def test_nao_permite_calculo_sem_tipo_servico():
    with pytest.raises(ValueError):
        calcular_orcamento(
            tipo_servico="",
            quantidade_clientes=1,
            metros_ramal=30,
            distancia=0,
            itens_materiais=[],
        )


def test_exportacao_csv_apos_calculo(tmp_path: Path):
    material = MaterialBase("COD2", "POSTE TESTE", "UN", 100.0)
    resultado = calcular_orcamento(
        tipo_servico="Ativação",
        quantidade_clientes=2,
        metros_ramal=30,
        distancia=10,
        itens_materiais=[ItemSelecionado(material=material, quantidade=2)],
    )

    destino = tmp_path / "orcamento.csv"
    exportar_orcamento_csv(resultado, destino)

    conteudo = destino.read_text(encoding="utf-8")
    assert "DADOS DO SERVIÇO" in conteudo
    assert "MATERIAIS SELECIONADOS" in conteudo
    assert "Total Geral" in conteudo


def test_formatar_moeda_ptbr():
    assert formatar_moeda(1234567.8) == "R$ 1.234.567,80"
