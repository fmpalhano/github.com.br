# github.com.br

Exportador CLI/GUI para gerar planilhas em formato pronto para SIPROG.

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

```bat
run_exportador.bat
```

No `.bat`, use `SELECIONAR_DATAS=1` para escolher as datas em janela (modo recomendado para independência operacional).

## Gerar executável (.exe)

No Windows, use o script abaixo para gerar o executável com PyInstaller:

```bat
build_exportador_exe.bat
```

Saída esperada:

- `dist\exportador_siprog.exe`

Duplo clique no `.exe` (sem argumentos) agora abre automaticamente:
- seleção de planilha/pasta,
- seleção das datas obrigatórias,
- painel de execução com logs.
- botão `Importar novamente` reativado automaticamente ao finalizar (sucesso, erro ou cancelamento).

> Assinado por: Felipe de Moraes Palhano.

## Argumentos

- `--arquivo`: arquivo Excel de origem (obrigatório quando `--selecionar-arquivos` não for usado).
- `--aba`: aba de leitura; se omitido, o sistema busca automaticamente `PROGRAMAÇÃO_OBRAS` ignorando acento/maiúsculas/espaços.
- `--selecionar-arquivos`: abre janela para selecionar planilha de entrada e pasta de saída.
- `--gui-execucao`: abre painel visual com logs em tempo real e barra de progresso.
- `--selecionar-datas`: abre janela para escolher `prazo_conclusao`, `data_programacao`, `data_inicio` e `data_fim`.
- `--data-coluna`: nome da coluna de data (padrão: `DATA`).
- `--data-inicio`: data inicial (`YYYY-MM-DD`).
- `--data-fim`: data final (`YYYY-MM-DD`).
- `--status-coluna`: nome da coluna de status (padrão: `STATUS`).
- `--status`: valor de status para filtrar.
- `--prazo-conclusao`: data fixa replicada em `PRAZO CONCLUSÃO`.
- `--data-programacao`: data fixa replicada em `DATA PROGRAMAÇÃO`.
- `--saida`: caminho do arquivo final.

## Comportamento

- Pipeline único e determinístico: selecionar arquivo/pasta, carregar aba alvo, aplicar filtros, transformar, exportar.
- Busca resiliente da aba `PROGRAMAÇÃO_OBRAS` (normalização de acentos/case/espaços).
- Sem integração de I.A.
- O caminho absoluto do XLSX final é exibido nos logs.
