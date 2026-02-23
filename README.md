# github.com.br

Exportador CLI para gerar planilhas em formato pronto para SIPROG.

## Uso

```bash
python exportador.py \
  --arquivo modeloProgramacao.xlsx \
  --data-inicio 2026-02-01 \
  --data-fim 2026-02-20 \
  --status ATIVO \
  --colunas equipe,tecnico,Data \
  --saida exportacao_siprog.xlsx
```

## Argumentos

- `--arquivo` (obrigatório): arquivo Excel de origem.
- `--aba`: nome ou índice da aba para leitura.
- `--data-coluna`: nome da coluna de data (padrão: `Data`).
- `--data-inicio`: data inicial (`YYYY-MM-DD`).
- `--data-fim`: data final (`YYYY-MM-DD`).
- `--status-coluna`: nome da coluna de status (padrão: `Status`).
- `--status`: valor de status para filtrar.
- `--colunas`: lista de colunas separadas por vírgula.
- `--saida`: caminho do arquivo final (padrão: `exportacao_siprog.xlsx`).

## Comportamento

- Filtro de data/status só é aplicado se a coluna existir.
- Se `--colunas` incluir coluna inexistente, o comando falha com erro explícito.
- O script exibe o caminho do arquivo gerado e a quantidade de registros exportados.
