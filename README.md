# Sistema PROFISSIONAL de Orçamento para Obra Eletrica (Tkinter)

Aplicação desktop com GUI única, base interna de materiais, editor avançado embutido e exportação CSV padronizada.

## Fluxo obrigatório

**Selecionar → Calcular → Visualizar → Exportar**

- Exportação só é liberada após o cálculo.
- Não há importação de planilhas externas para materiais.

## Recursos principais

- Tipo de serviço:
  - Obra Eletrica
  - Ativacao Eletrica
  - Lancamento de Cabo Eletrico
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
- Catálogo interno expandido com materiais elétricos (descrição + unidade) incorporados ao código, sem planilha externa.

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

### Regras críticas da exportação

- O arquivo é gerado em **UTF-8 com BOM** (`utf-8-sig`) para evitar corrupção de acentuação no Excel, e inclui a diretiva `sep=,` para garantir abertura correta em colunas no Excel pt-BR.
- As colunas **CHAVE**, **DATA** e **PEP** são sempre exportadas vazias (`""`) para preenchimento automático na planilha destino.
- `VALOR_UNITÁRIO` vem diretamente da base (material/serviço), sem recálculo por divisão.
- Cada material selecionado gera exatamente uma linha no CSV.
- Para evitar corrupcao de encoding no destino, os valores textuais sao exportados sem acentos.
- `VALOR_REALIZADO = VALOR_UNITÁRIO × QTD_REALIZADO`
- `VALOR_TOTAL = VALOR_REALIZADO + CALC. TRANSPORTE`
- `DIFERENÇA = VALOR_TOTAL - VALOR_REALIZADO`

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


### Observacoes de build do EXE

- O build usa como entrada `src\orcamento_obra.py` (nao usa `-m`), que e o formato correto do PyInstaller.
- O script limpa `build/`, `dist/` e `.spec` antes de gerar para evitar residuos de builds anteriores.
- Em caso de erro, o `gerar_exe.bat` finaliza com codigo de falha (`exit /b 1`).
