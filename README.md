# Sistema de Orçamento Telecom (Tkinter)

Aplicação desktop com **tela única** para orçamento de serviços de telecomunicações.

## Princípios do sistema

- Base de materiais **interna e fixa** (não há importação de planilhas para materiais).
- Fluxo obrigatório: **selecionar → calcular → visualizar → exportar**.
- Exportação liberada somente após o cálculo.

## Funcionalidades

### 1) Materiais (base interna)

A aplicação carrega automaticamente os materiais da base interna (`src/base_materiais.py`), contendo:

- Código do material
- Descrição
- Unidade de medida
- Valor unitário

Na GUI, o usuário apenas:

- seleciona os materiais (checkbox)
- informa a quantidade de cada material

> Não é possível importar planilha de materiais nem editar a base pela interface.

### 2) Tela única (Tkinter)

Componentes presentes:

- Tipo de Serviço (`Ativação`, `Obra`, `Lançamento de Cabo`)
- Quantidade de clientes
- Metros por ramal
- Distância
- Lista completa de materiais da base interna
- Preview do orçamento

Botões:

- **Calcular Orçamento**
- **Exportar para Planilha**
- **Limpar**

### 3) Regras de negócio implementadas

- `Metragem_Final = max(30, Qtd_Clientes × Metros_Ramal) × 1.05`
- Para **Lançamento de Cabo**, a quantidade de serviço usa conversão para KM (`metros / 1000`).
- Valor total:
  - Valor do serviço = Quantidade calculada × Valor unitário do serviço
  - Valor dos materiais = soma(Qtd × Valor unitário)
  - Valor total = Serviço + Materiais
- O cálculo não é permitido sem tipo de serviço selecionado.

### 4) Exportação

- Exportação em CSV por botão explícito **Exportar para Planilha**.
- Disponível apenas após cálculo.
- Arquivo exportado inclui:
  - dados do serviço
  - materiais selecionados
  - quantidades
  - valores unitários
  - total por item
  - total geral

## Execução

### Windows

Dê duplo clique em `executar_orcamento.bat`.

### Terminal

```bash
python src/orcamento_obra.py
```
