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

1. Abra a pasta `recipro`.
2. Dê duplo clique em `run_recipro.bat`.
3. O script cria/usa `.venv`, instala dependências e inicia o servidor.
4. O launcher tenta Python na ordem: `3.11` → `3.10` → `3.x` padrão (`py -3`) → `python`.
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
