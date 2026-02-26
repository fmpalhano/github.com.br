# Sistema PROFISSIONAL de Orçamento para Obra Elétrica (Tkinter)

Aplicação desktop com GUI única, base interna de materiais, editor avançado embutido e exportação CSV padronizada.

## Fluxo obrigatório

**Selecionar → Calcular → Visualizar → Exportar**

- Exportação só é liberada após o cálculo.
- Não há importação de planilhas externas para materiais.

## Recursos principais

- Tipo de serviço:
  - Obra Elétrica
  - Ativação Elétrica
  - Lançamento de Cabo Elétrico
- Seleção de serviço por tipo
- Campos numéricos (clientes, metros por ramal, distância km)
- Lista completa de materiais com:
  - pesquisa por código/descrição
  - rolagem
  - seleção e quantidade
- Preview do orçamento
- Editor de materiais (modo avançado):
  - adicionar
  - editar
  - remover
  - salvar/cancelar
- Persistência local em `data/materiais_base.json`

## Regras de negócio implementadas

- `Metragem_Final = max(30, Qtd_Clientes × Metros_Ramal) × 1.05`
- Lançamento de cabo converte metragem para KM (`m / 1000`)
- `Valor serviço = quantidade calculada × valor unitário do serviço`
- `Valor materiais = soma(qtd × valor unitário)`
- `Valor transporte = distância_km × 12.00`
- `Valor total = serviço + materiais + transporte`

## Exportação CSV (ordem exata)

A exportação segue exatamente as colunas:

`CHAVE, DATA, SUPERVISOR, EQUIPE, PEP, DESCRIÇÃO OBRA, ENCARREGADO, TIPO SERVIÇO, SERVIÇO, MATERIAL, QTD, GPS POSTE, SERVIÇO_REALIZADO, QTD_REALIZADO, VALID_EVIDÊNCIA, RETORNO_META_Ñ_ALCANÇADA, VALOR_REALIZADO, VALOR_TOTAL, VALOR_UNITÁRIO, COD_SERVIÇO, COD_SIMULADOR, DISTANCIA, CALC. TRANSPORTE, DIFERENÇA`

## Execução

```bash
python -m src.orcamento_obra
```

No Windows, também é possível usar:

- `executar_orcamento.bat`

## Distribuição EXE (standalone)

Use o script:

- `gerar_exe.bat`

Ele gera um executável **independente** em `dist\OrcamentoObraEletrica.exe` (sem exigir Python instalado) usando `PyInstaller --onefile --windowed`.
