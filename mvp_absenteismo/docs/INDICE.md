# Documentação do app — Índice

Material para entender completamente o MVP de redução de absenteísmo (CPDI), escrito para **leigos e gestores**.

---

## Por onde começar?

| Se você quer… | Leia |
|---|---|
| Entender tudo de uma vez | **[Guia completo](GUIA_COMPLETO.md)** |
| Só a ideia e o objetivo | [01 — Ideia e objetivo](01_IDEA_E_OBJETIVO.md) |
| Ver o fluxo do início ao fim | [02 — Como funciona passo a passo](02_COMO_FUNCIONA_PASSO_A_PASSO.md) |
| Entender o machine learning | [03 — Como o modelo aprende](03_COMO_O_MODELO_APRENDE.md) |
| Usar a interface no navegador | [04 — Guia da interface](04_GUIA_DA_INTERFACE.md) |
| Decifrar um termo | [05 — Glossário](05_GLOSSARIO.md) |
| Respostas rápidas | [06 — Perguntas frequentes](06_PERGUNTAS_FREQUENTES.md) |
| Privacidade e ética | [07 — Ética e privacidade](07_ETICA_E_PRIVACIDADE.md) |
| Apresentar para outras pessoas | [Guia de explicação (apresentação)](../GUIA_EXPLICACAO_APP.md) |

---

## Ordem de leitura sugerida (leigo)

1. [Ideia e objetivo](01_IDEA_E_OBJETIVO.md) — 5 min  
2. [Como funciona passo a passo](02_COMO_FUNCIONA_PASSO_A_PASSO.md) — 10 min  
3. [Guia da interface](04_GUIA_DA_INTERFACE.md) — 10 min (com app aberto)  
4. [Como o modelo aprende](03_COMO_O_MODELO_APRENDE.md) — 15 min (opcional, mais detalhe)  
5. [Glossário](05_GLOSSARIO.md) ou [FAQ](06_PERGUNTAS_FREQUENTES.md) — consulta  

---

## Ordem de leitura sugerida (gestor / apresentação)

1. [Ideia e objetivo](01_IDEA_E_OBJETIVO.md)  
2. [Guia completo](GUIA_COMPLETO.md) — seções 1–3 e 9–11  
3. [Guia de explicação](../GUIA_EXPLICACAO_APP.md) — roteiro de demo  
4. [Ética e privacidade](07_ETICA_E_PRIVACIDADE.md) — se perguntarem sobre LGPD  

---

## Documentos na raiz do projeto

| Arquivo | Conteúdo |
|---|---|
| [README.md](../README.md) | Instalação, execução técnica, arquitetura resumida |
| [GUIA_EXPLICACAO_APP.md](../GUIA_EXPLICACAO_APP.md) | Roteiro para apresentar o app a stakeholders |

---

## Mapa: documentação ↔ código

| Tema | Documento | Código |
|---|---|---|
| Dados | [Guia completo §4](GUIA_COMPLETO.md#4-de-onde-vêm-os-dados) | `src/gerar_dados.py` |
| Modelo preditivo | [03 — Como o modelo aprende](03_COMO_O_MODELO_APRENDE.md) | `src/modelo_preditivo.py` |
| Faixas de risco | [Guia completo §6](GUIA_COMPLETO.md#6-classificação-de-risco-e-ações-recomendadas) | `src/decisao.py` |
| Confirmações | [Guia completo §7](GUIA_COMPLETO.md#7-priorização-de-confirmações-quem-ligar) | `src/decisao.py` |
| Agenda | [Guia completo §8](GUIA_COMPLETO.md#8-otimização-da-agenda-onde-encaixar-cada-paciente) | `src/otimizacao_agenda.py` |
| Interface | [04 — Guia da interface](04_GUIA_DA_INTERFACE.md) | `app.py` |
| Pipeline CLI | [README](../README.md) | `src/pipeline.py` |

---

## Executar o app

```bash
cd mvp_absenteismo
pip install -r requirements.txt
python -m streamlit run app.py
```

Abrir: **http://localhost:8501**
