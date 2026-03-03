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
