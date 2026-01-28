# github.com.br

Template inicial para relatório de obra em formato DOCX, usando placeholders para geração automática.

## Arquivos

- `docs/template-obra.md`: modelo de template com campos configuráveis.

## Como testar

1. Copie `docs/template-obra.md` para um arquivo temporário (ex.: `relatorio.md`).
2. Substitua manualmente alguns placeholders por valores reais (ex.: `{{titulo_obra}}`, `{{data_relatorio}}`).
3. Converta o Markdown para DOCX usando uma ferramenta como o pandoc:

```bash
pandoc relatorio.md -o relatorio.docx
```

4. Abra o `relatorio.docx` e valide se o conteúdo e a formatação batem com o esperado.
