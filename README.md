# github.com.br

Exportador CLI para gerar planilhas em formato pronto para SIPROG.

## Uso

```bash
python exportador.py \
  --arquivo modeloProgramacao.xlsx \
  --data-inicio 2026-02-01 \
  --data-fim 2026-02-20 \
  --status LIB/LOG \
  --saida exportacao_siprog.xlsx
```

## Teste rápido no Windows (.bat)

Para facilitar o teste operacional, use o arquivo `run_exportador.bat`:

```bat
run_exportador.bat
```

Ele já chama o `exportador.py` com parâmetros de exemplo (arquivo, período, status e saída).
Se precisar, edite as variáveis no topo do `.bat` antes de executar.

> Se a janela abrir e fechar rápido no Windows: o `.bat` agora usa `PAUSAR_NO_FINAL=1` por padrão, então a mensagem de erro/sucesso fica visível até você pressionar uma tecla.

## Argumentos

- `--arquivo` (obrigatório): arquivo Excel de origem.
- `--aba`: nome ou índice da aba para leitura.
- `--data-coluna`: nome da coluna de data (padrão: `DATA PROGRAMAÇÃO`).
- `--data-inicio`: data inicial (`YYYY-MM-DD`).
- `--data-fim`: data final (`YYYY-MM-DD`).
- `--status-coluna`: nome da coluna de status (padrão: `STATUS SAP`).
- `--status`: valor de status para filtrar.
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

- O exportador valida e exige todas as colunas obrigatórias do layout SIPROG.
- O mapeamento de colunas tolera variação de espaços e tipos de travessão (`-`, `–`, `—`).
- Filtros de data/status falham com erro explícito se a coluna indicada não existir.
- O script exibe o caminho do arquivo gerado e a quantidade de registros exportados.
