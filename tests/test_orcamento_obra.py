from src.orcamento_obra import (
    ItemOrcamento,
    MaterialCatalogo,
    OrcamentoMateriais,
    formatar_moeda,
    gerar_relatorio,
)


def test_calculo_total_geral_materiais():
    itens = [
        ItemOrcamento(cod_lista="A", quantidade=2, preco_unitario=100.0),
        ItemOrcamento(cod_lista="B", quantidade=3, preco_unitario=50.0),
    ]
    orcamento = OrcamentoMateriais(itens=itens, taxa_imprevistos_percentual=10)

    assert orcamento.subtotal == 350.0
    assert orcamento.valor_imprevistos == 35.0
    assert orcamento.total_geral == 385.0


def test_relatorio_com_item_nao_encontrado():
    orcamento = OrcamentoMateriais(
        itens=[ItemOrcamento(cod_lista="X1", quantidade=1, preco_unitario=25.0)]
    )
    catalogo = {
        "A1": MaterialCatalogo(
            ativacao="",
            linha_viva="ITEM A1",
            tipo_estr="",
            cod_lista="A1",
            resumo="POSTE",
            prioridade=1,
        )
    }

    relatorio = gerar_relatorio(orcamento, catalogo)
    assert "CÓDIGO NÃO ENCONTRADO NO CATÁLOGO" in relatorio


def test_formatar_moeda_ptbr():
    assert formatar_moeda(1234567.8) == "R$ 1.234.567,80"
