# github.com.br
Git pessoal para projetos aplicados aos trabalhos que me incluo.

## Programa: Cálculo de Obra (somente materiais em Tkinter)

Agora o programa roda em **uma interface única Tkinter** (desktop), focada apenas em materiais.

### Campos usados

#### Catálogo de materiais (CSV)
- `ATIVACAO`
- `LINHA_VIVA`
- `TIPOESTR`
- `CODLISTA`
- `RESUMO`
- `PRIORIDADE`

#### Itens do orçamento (CSV)
- `CODLISTA`
- `QUANTIDADE`
- `PRECO_UNITARIO`

## Como executar

### Opção 1 (Windows): arquivo `.bat`

Clique duas vezes em `executar_orcamento.bat`.

### Opção 2 (terminal)

```bash
python src/orcamento_obra.py
```

## Como usar a tela

1. Selecione o CSV de catálogo.
2. Selecione o CSV de itens do orçamento.
3. Informe o percentual de imprevistos.
4. Clique em **Calcular orçamento**.
5. O relatório completo será exibido na caixa de texto.

## Arquivos de exemplo

- `catalogo_materiais_exemplo.csv`
- `orcamento_materiais_exemplo.csv`

## Resultado do relatório

- detalhe por item (código, descrição, tipo, prioridade, quantidade, preço e subtotal)
- subtotal de materiais
- valor de imprevistos
- total geral
