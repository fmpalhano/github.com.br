from src.base_materiais import materiais_padrao


def test_materiais_padrao_retorna_lista_enriquecida():
    materiais = materiais_padrao()
    assert len(materiais) > 50


def test_materiais_padrao_sem_codigos_duplicados():
    materiais = materiais_padrao()
    codigos = [m["codigo"] for m in materiais]
    assert len(codigos) == len(set(codigos))
