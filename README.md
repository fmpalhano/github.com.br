# github.com.br

Template inicial para relatório de obra em formato DOCX, usando placeholders para geração automática e um gerador em Python com IA online.

## Arquivos

- `docs/template-obra.md`: modelo de template com campos configuráveis.
- `generate_report.py`: script em Python que usa IA online para preencher o template.
- `requirements.txt`: dependências do gerador.

## Como gerar com IA (Python)

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

> **Atenção:** o pacote correto é `openai` (com **AI**), não `openia`. Se aparecer erro como
> `No matching distribution found for openia`, corrija o comando e execute novamente.

2. Defina a variável de ambiente `OPENAI_API_KEY`.

```bash
export OPENAI_API_KEY="sua-chave"
```

3. Rode o gerador passando a descrição da obra:

```bash
python generate_report.py \\
  --prompt "Relatório de obra com nome, localidade, status PEP e registros fotográficos."
```

4. Para converter o Markdown gerado em DOCX (requer `pandoc`):

```bash
python generate_report.py \\
  --prompt "Relatório completo da obra com medições e dificuldades." \\
  --convert-docx
```

5. Para salvar o JSON retornado pela IA:

```bash
python generate_report.py \\
  --prompt "Relatório de obra com cronograma." \\
  --output-json relatorio.json
```

### Executar sem IA (usando JSON pronto)

Se você já tiver os dados estruturados, pode pular a chamada à IA:

```bash
python generate_report.py --data-json relatorio.json
```

## Como testar

1. Copie `docs/template-obra.md` para um arquivo temporário (ex.: `relatorio.md`).
2. Substitua manualmente alguns placeholders por valores reais (ex.: `{{titulo_obra}}`, `{{data_relatorio}}`).
3. Converta o Markdown para DOCX usando uma ferramenta como o pandoc:

```bash
pandoc relatorio.md -o relatorio.docx
```

4. Abra o `relatorio.docx` e valide se o conteúdo e a formatação batem com o esperado.
