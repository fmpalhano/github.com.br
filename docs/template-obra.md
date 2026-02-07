# Template de Relatório de Obra (DOCX)

> Este arquivo é um guia de template com placeholders para geração automática em DOCX.
> Os campos entre `{{ }}` devem ser preenchidos pelo sistema.

## Capa

**Título da obra:** {{titulo_obra}}

**Cliente/Concessionária:** {{cliente}}

**Localidade:** {{localidade}}

**Data do relatório:** {{data_relatorio}}

**Imagem de capa (opcional):** {{imagem_capa}}

---

## Informações gerais da obra

**Descrição da obra:**
{{descricao_obra}}

**Extensão total da obra:**
- MT: {{extensao_mt_km}} km
- BT: {{extensao_bt_km}} km
- Total de postes: {{total_postes}}

---

## Status elemento PEP

{{#pep_partes}}
**Parte:** {{parte_nome}}
- Obra: {{obra}}
- PEP: {{pep}}
- Poste: {{poste}}
- Status: {{status}}

{{/pep_partes}}

---

## Considerações / Ressalvas

{{consideracoes_ressalvas}}

---

## Materiais

{{materiais}}

---

## Execução

**Início da obra:** {{data_inicio}}

**Previsão de conclusão/energização:** {{data_previsao_conclusao}}

**Estrutura/equipamentos utilizados:**
{{#equipamentos}}
- {{item}}
{{/equipamentos}}

**Dificuldades:**
{{#dificuldades}}
- {{item}}
{{/dificuldades}}

**Curva S de acompanhamento geral da obra:**
{{curva_s}}

**Observações finais:**
{{observacoes_finais}}

---

## KPI da obra

**Resumo:**
{{kpi_resumo}}

**Indicadores:**
{{#kpi_indicadores}}
- {{nome}}: {{valor}} {{unidade}}
{{/kpi_indicadores}}

**Imagens de KPI:**
{{#imagens_kpi}}
![{{legenda}}]({{caminho}})
{{/imagens_kpi}}

---

## Registros fotográficos da obra

{{#registros_fotograficos}}
**Seção:** {{secao}}

| Foto | Descrição |
| ---- | --------- |
{{#itens}}
| {{foto}} | {{descricao}} |
{{/itens}}

{{/registros_fotograficos}}

---

## Imagens gerais do relatório

{{#imagens_relatorio}}
![{{legenda}}]({{caminho}})
{{/imagens_relatorio}}

---

## Anexo DWG (quando aplicável)

Arquivo: {{dwg_arquivo}}
