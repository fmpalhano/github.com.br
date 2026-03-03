# Recipro Evolution

Aplicação web para análise de reciprocidade emocional em conversas WhatsApp exportadas em `.txt`.

## Rodar localmente (Linux/macOS)

```bash
cd recipro
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Rodar localmente (Windows com 1 clique)

## Launcher automático no Windows (BAT/PowerShell)

### Opção 1 — BAT (duplo clique)
- Arquivo: `run_recipro.bat`
- O script:
  - detecta Python 3.10+
  - cria/usa `venv` no diretório do projeto
  - instala dependências na primeira execução
  - inicia o FastAPI em `http://127.0.0.1:8000` com reload

### Opção 2 — PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File .\run_recipro.ps1
```

### Variáveis úteis
- `FORCE_INSTALL=1` força reinstalação das dependências
- `AUTO_RESTART=1` reinicia o servidor automaticamente se cair

Exemplo (Prompt de Comando):
```bat
set FORCE_INSTALL=1
set AUTO_RESTART=1
run_recipro.bat
```

1. Abra a pasta `recipro`.
2. Dê duplo clique em `run_recipro.bat`.
3. O script cria/usa `venv`, instala dependências e inicia o servidor.
4. O launcher tenta Python na ordem: `3.14` → `3.13` → `3.12` → `3.11` → `3.10` → `python`.
5. Na primeira execução ele instala dependências; nas próximas, ele detecta instalação pronta e inicia mais rápido.
6. Para forçar reinstalação: `set FORCE_INSTALL=1 && run_recipro.bat`.


## Logs de execução (Windows)

- Cada execução do `run_recipro.bat` gera um log em `recipro/logs/` com nome no formato `run_YYYYMMDD_HHMMSS.log`.
- Se o servidor não subir, abra esse arquivo e me envie o conteúdo para diagnóstico.
- O launcher agora valida import dos módulos críticos (`fastapi`, `uvicorn`, `pandas`, `spacy`, `textblob`, `sqlalchemy`, `reportlab`, `main`) antes de subir o servidor e aponta erro no log se algo estiver inconsistente.

## Testar no celular (100% web)

1. Conecte **PC e celular na mesma rede Wi‑Fi**.
2. Inicie o app com `run_recipro.bat` (Windows) ou comando `uvicorn` com `--host 0.0.0.0`.
3. No terminal, pegue o IP local do PC (ex.: `192.168.0.15`).
4. No navegador do celular, abra:

```text
http://SEU_IP_LOCAL:8000
```

Exemplo:

```text
http://192.168.0.15:8000
```

### Se não abrir no celular

- Verifique se firewall do Windows permite Python/Uvicorn na rede privada.
- Confirme que ambos estão no mesmo Wi‑Fi (sem rede guest isolada).
- Teste no próprio PC com `http://127.0.0.1:8000`.

## Observação de privacidade

- O arquivo `.txt` é apagado após o processamento.
- Mensagens não são armazenadas; apenas métricas agregadas são persistidas.


### Se aparecer `ERROR: Operation cancelled by user`

- Se ainda não abrir após instalar Python, rode `set FORCE_INSTALL=1 && run_recipro.bat` para reinstalar dependências e regenerar o ambiente.
- Isso significa que a instalação do `pip` foi interrompida manualmente.
- Execute `run_recipro.bat` novamente e aguarde até o final da instalação.
- Depois da primeira instalação completa, as próximas execuções não reinstalam tudo.


## BAT oficial (entrega final)

Arquivo: `run_recipro.bat`

### Como usar (duplo clique)
1. Abra a pasta `recipro`.
2. Dê duplo clique em `run_recipro.bat`.
3. Aguarde as etapas `1/5` até `5/5`.

### O que ele mostra no terminal
- Python selecionado
- Status da venv
- Status da instalação de dependências
- Endpoint ativo (`http://127.0.0.1:8000`)

### Ajustes rápidos
- Forçar reinstalação:
```bat
set FORCE_INSTALL=1
run_recipro.bat
```
- Reinício automático se cair:
```bat
set AUTO_RESTART=1
run_recipro.bat
```

### Log detalhado
- Caminho: `recipro\logs\run_YYYYMMDD_HHMMSS.log`
- Se falhar, envie esse arquivo para diagnóstico.


### Correção do erro "nao pode localizar o rotulo em lote"
- O `run_recipro.bat` foi refeito em formato ASCII + CRLF e sem `call :run_server`.
- Agora o servidor inicia por fluxo direto com rótulo único `:server_loop`, evitando o erro de rótulo ausente.
