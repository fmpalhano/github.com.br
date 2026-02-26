# github.com.br
Git pessoal para projetos aplicados aos trabalhos que me incluo.

## Programa: Cálculo de Obra (somente materiais)

O programa foi ajustado para trabalhar **apenas com materiais**.

Ele usa dois arquivos CSV:

1. **Catálogo de materiais** (com os campos recebidos da sua base):
   - `ATIVACAO`
   - `LINHA_VIVA`
   - `TIPOESTR`
   - `CODLISTA`
   - `RESUMO`
   - `PRIORIDADE`
2. **Itens do orçamento**:
   - `CODLISTA`
   - `QUANTIDADE`
   - `PRECO_UNITARIO`

## Como executar

```bash
python3 src/orcamento_obra.py \
  --catalogo-csv catalogo_materiais_exemplo.csv \
  --orcamento-csv orcamento_materiais_exemplo.csv \
  --imprevistos 8
```

## Saída

O relatório apresenta por item:

- código (`CODLISTA`)
- descrição (priorizando `LINHA_VIVA` e depois `ATIVACAO`)
- tipo (`RESUMO`/`TIPOESTR`)
- prioridade
- subtotal do item

E também os totais:

- subtotal de materiais
- valor de imprevistos
- total geral

## Arquivos de exemplo

- `catalogo_materiais_exemplo.csv`
- `orcamento_materiais_exemplo.csv`
