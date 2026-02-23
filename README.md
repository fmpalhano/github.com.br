# github.com.br

Exportador CLI para gerar planilhas em formato pronto para SIPROG.

## Uso

```bash
python exportador.py \
  --arquivo modeloProgramacao.xlsx \
  --data-inicio 2026-02-01 \
  --data-fim 2026-02-20 \
  --status LIB/LOG \
  --prazo-conclusao 31/03/2026 \
  --data-programacao 23/02/2026 \
  --saida exportacao_siprog.xlsx
```

## Teste rápido no Windows (.bat)

Para facilitar o teste operacional, use o arquivo `run_exportador.bat`:

```bat
run_exportador.bat
```

Ele já chama o `exportador.py` com parâmetros de exemplo (arquivo, período, status e saída).
Se precisar, edite as variáveis no topo do `.bat` antes de executar.

- `MODO_TELA=1`: abre uma tela para escolher a planilha e a pasta de trabalho.
- `MODO_TELA=0`: usa o caminho fixo definido em `ARQUIVO_ENTRADA`.
- `ESCOLHER_ABA=1`: lista as abas e permite selecionar manualmente qual aba exportar.
- `ESCOLHER_ABA=0`: usa a aba definida por `--aba` (ou a primeira aba, por padrão).
- `GUI_COLUNAS=1`: abre uma janela para pesquisar colunas e visualizar amostras de valores.
- `GUI_COLUNAS=0`: desativa a visualização GUI de colunas.
- `GUI_EXECUCAO=1`: abre painel visual com logs em tempo real e barra de loading/status.
- `GUI_EXECUCAO=0`: executa somente no terminal.
- `PRAZO_CONCLUSAO`: valor usado para preencher `PRAZO CONCLUSÃO` em todas as linhas.
- `DATA_PROGRAMACAO`: valor usado para preencher `DATA PROGRAMAÇÃO` em todas as linhas.

> Se a janela abrir e fechar rápido no Windows: o `.bat` usa `PAUSAR_NO_FINAL=1` por padrão, então a mensagem de erro/sucesso fica visível até você pressionar uma tecla.

## Argumentos

- `--arquivo`: arquivo Excel de origem (obrigatório quando `--selecionar-arquivos` não for usado).
- `--aba`: nome ou índice da aba para leitura.
- `--selecionar-aba`: mostra lista de abas para seleção manual durante a execução.
- `--gui-colunas`: abre interface para pesquisar colunas e visualizar amostras dos dados da aba antes de exportar.
- `--gui-execucao`: abre painel de execução com logs em tempo real e barra de progresso.
- `--data-coluna`: nome da coluna de data (padrão: `DATA PROGRAMAÇÃO`).
- `--data-inicio`: data inicial (`YYYY-MM-DD`).
- `--data-fim`: data final (`YYYY-MM-DD`).
- `--status-coluna`: nome da coluna de status (padrão: `STATUS SAP`).
- `--status`: valor de status para filtrar.
- `--prazo-conclusao`: data fixa replicada em `PRAZO CONCLUSÃO`.
- `--data-programacao`: data fixa replicada em `DATA PROGRAMAÇÃO`.
- `--colunas`: colunas adicionais (separadas por vírgula) para incluir no final.
- `--saida`: caminho do arquivo final (padrão: `exportacao_siprog.xlsx`).

## Layout obrigatório SIPROG

As colunas abaixo **sempre** são exportadas (na ordem) e devem existir na planilha de origem:

- `CAPEX/OPEX`
- `NOTA PROJETO - SOMENTE CAPEX`
- `NOTA CLIENTE - SOMENTE CAPEX`
- `NOME OBRA - SOMENTE CAPEX`
- `COD. PROGRAMAÇÃO - SOMENTE OPEX`
- `EQP. NOVO? – SOMENTE OPEX`
- `SE / ORIGEM LTDA – SOMENTE OPEX`
- `LOCAL INSTAL. – SOMENTE OPEX`
- `DATA INSPEÇÃO – SOMENTE OPEX`
- `ORDEM INSPEÇÃO – SOMENTE OPEX`
- `PRIORIDADE – SOMENTE OPEX`
- `CLASSE – SOMENTE OPEX`
- `DESCRIÇÃO ANOMALIA – SOMENTE OPEX`
- `REGIONAL`
- `PARCEIRA`
- `EQUIPE`
- `REFERÊNCIA`
- `PRAZO CONCLUSÃO`
- `DATA PROGRAMAÇÃO`
- `QUANTIDADES DIAS`
- `ELEMENTO PEP – SOMENTE CAPEX`
- `ORDEM SERVIÇO – SOMENTE OPEX`
- `ORÇAMENTO MAT.`
- `ORÇAMENTO MO`
- `VALOR MÃO DE OBRA PROGRAMADA`
- `TURNO`
- `COM RECLAMAÇÃO?`
- `ORIGEM RECLAMAÇÃO`
- `TIPO SERVIÇO`
- `TEM RESTRIÇÃO?`
- `OBRA VALIDADA EM CAMPO?`
- `STATUS SAP`
- `MUNICIPIO – SOMENTE CAPEX`
- `BAIRRO – SOMENTE CAPEX`
- `DESCRIÇÃO PI – SOMENTE CAPEX`
- `REGULADO ANEEL`
- `BARRAMENTO/CD. EQUIPAMENTO – SOMENTE OPEX`
- `TIPO INTERVENÇÃO`
- `NÚMERO SI – SOMENTE BLOQUEIO DO ALIMENTADOR (LINHA VIVA) e DESLIGAMENTO PROGRAMADO`
- `INICIO PREVISTO – SOMENTE DESLIGAMENTO PROGRAMADO`
- `FINAL PREVISTO – SOMENTE DESLIGAMENTO PROGRAMADO`
- `SERVIÇOS`
- `OBSERVAÇÃO`

## Comportamento

- A aba padrão processada é `PROGRAMACAO_OBRAS` (quando `--aba` não é informado).
- O exportador valida e exige todas as colunas obrigatórias do layout SIPROG.
- O mapeamento de colunas tolera variação de espaços e tipos de travessão (`-`, `–`, `—`).
- Avisos visuais do `openpyxl` sobre extensões de formatação/validação são suprimidos na leitura para não poluir a execução operacional.
- Filtros de data/status falham com erro explícito se a coluna indicada não existir.
- A interface GUI de colunas permite localizar informações esparsas e selecionar colunas extras visualmente.
- A transformação aplica regras de negócio para CAPEX/OPEX, campos fixos e limpeza numérica de PEP/notas antes da exportação.
- O script exibe o caminho do arquivo gerado e a quantidade de registros exportados.
