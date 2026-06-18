# Absenteísmo — MVP CPDI

MVP de estratégia inteligente para redução de absenteísmo em clínica de diagnóstico por imagem.

O código da aplicação está em [`mvp_absenteismo/`](mvp_absenteismo/). Consulte o [README do MVP](mvp_absenteismo/README.md) para instalação local, arquitetura e documentação completa.

## Deploy (Railway)

Este repositório inclui `requirements.txt`, `start.sh` e `railway.toml` na raiz para o Railpack detectar Python e subir o Streamlit.

**Start command (se configurar manualmente no painel):**

```bash
bash start.sh
```

**Alternativa:** defina **Root Directory** = `mvp_absenteismo` no Railway e use:

```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```
