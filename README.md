# github.com.br

Template inicial para relatório de obra em formato DOCX, usando placeholders para geração automática e um gerador em Python com IA online.

## Arquivos

- `docs/template-obra.md`: modelo de template com campos configuráveis.
- `generate_report.py`: script em Python que usa IA online para preencher o template.
- `requirements.txt`: dependências do gerador.
- `docs/ui/index.html`: interface visual para montar o comando rapidamente.
- `run_ui.bat`: atalho Windows para subir a interface localmente.
- `app_server.py`: servidor local que executa o relatório ao clicar no botão.
- `build_windows_installer.bat`: gera um executável Windows para rodar sem Python.

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

> Dica: use `--log-file relatorio.log` para salvar os logs em arquivo e acompanhar o contador no final.

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

## Interface visual (Grupo Setup)

Abra a interface local para executar o relatório diretamente:

```bash
python app_server.py
```

Depois acesse `http://localhost:8000` no navegador.

### Imagens, KPI e DWG

A interface permite anexar imagens para o relatório e para o KPI, além de um arquivo DWG. Esses
arquivos são adicionados ao template padrão em seções dedicadas e mantêm o layout A4.

### Modo offline (gratuito)

Se você quiser gerar sem consumir créditos, ative o **Modo offline** na interface. Nesse modo,
o relatório é gerado sem chamada à IA e a descrição informada é usada como base do conteúdo.

### Atalho no Windows

Se preferir, execute o arquivo `run_ui.bat` para iniciar o servidor automaticamente.

### Executável Windows (sem Python)

Para demonstrar sem instalar Python, execute:

```bat
build_windows_installer.bat
```

O executável será criado em `dist/GrupoSetupRelatorios.exe`.

## Como testar

1. Copie `docs/template-obra.md` para um arquivo temporário (ex.: `relatorio.md`).
2. Substitua manualmente alguns placeholders por valores reais (ex.: `{{titulo_obra}}`, `{{data_relatorio}}`).
3. Converta o Markdown para DOCX usando uma ferramenta como o pandoc:

```bash
pandoc relatorio.md -o relatorio.docx
```

4. Abra o `relatorio.docx` e valide se o conteúdo e a formatação batem com o esperado.
