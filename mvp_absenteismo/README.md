# MVP — Estrategia Inteligente para Reducao do Absenteismo (CPDI)

Implementacao funcional da proposta de reducao de absenteismo em clinica de
diagnostico por imagem. Cobre as tres camadas descritas no documento:
preditiva, decisoria e de otimizacao, com pipeline executavel de ponta a ponta.

## Arquitetura

```
Dados historicos
      |
      v
[Camada preditiva]      modelo_preditivo.py   -> p_i = P(falta)
      |
      v
[Camada decisoria]      decisao.py            -> faixa de risco + acao
      |                                          priorizacao de confirmacao (mochila)
      v
[Camada de otimizacao]  otimizacao_agenda.py  -> PLI: aloca agenda
      |
      v
Agenda inteligente + acoes preventivas
```

Mapeamento direto com as secoes da proposta:

| Secao da proposta | Modulo |
|---|---|
| 7. Dados necessarios | `src/gerar_dados.py` (base sintetica realista) |
| 8. Modelo preditivo (logit + boosting + metricas) | `src/modelo_preditivo.py` |
| 9. Classificacao por nivel de risco (Tabela 1) | `src/decisao.py::classificar_risco` |
| 10. Otimizacao da agenda (PLI) | `src/otimizacao_agenda.py` |
| 11. Otimizacao das acoes de confirmacao | `src/decisao.py::otimizar_confirmacoes` |
| 13. Indicadores de desempenho | `src/pipeline.py::imprimir_indicadores` |

## Instalacao

```bash
pip install -r requirements.txt
```

O projeto usa o solver HiGHS por padrao, compativel com Linux, Windows e
macOS Apple Silicon. CBC continua disponivel como alternativa quando estiver
instalado no ambiente.

## Execucao

```bash
# 1. gerar base sintetica (substituir pela base real da clinica depois)
python -m src.gerar_dados --n 8000 --saida data/agendamentos.csv

# 2. treinar e avaliar modelos preditivos
python -m src.modelo_preditivo --dados data/agendamentos.csv

# 3. rodar o pipeline completo (predicao + risco + confirmacao + agenda)
python -m src.pipeline --dados data/agendamentos.csv --lam 2.0 --orcamento 200

# 4. testes de regressao
pytest -q
```

## Interface grafica

Aplicacao Streamlit interativa com quatro abas (visao geral, risco,
confirmacoes e agenda) e controles em tempo real para orcamento,
capacidade, overbooking e lambda.

```bash
pip install -r requirements.txt
streamlit run app.py
```

A app abre no navegador em `http://localhost:8501`. Na primeira execucao
ela gera a base sintetica (se ainda nao existir) e treina o modelo uma
unica vez, persistindo em `data/modelo.joblib`. As execucoes seguintes
carregam o modelo salvo e respondem de forma instantanea aos controles.

Abas:
- **Visao geral**: indicadores do dia, desempenho dos modelos e grafico
  dos principais fatores de risco.
- **Risco**: distribuicao por faixa (Tabela 1), histograma de
  probabilidades e tabela filtravel de agendamentos escorados.
- **Confirmacoes**: priorizacao das acoes ativas sob orcamento, com
  dispersao risco x receita destacando quem recebe intervencao.
- **Agenda**: otimizacao da alocacao (PLI), mapa de calor de ocupacao
  por horario x modalidade e lista de alocacoes.

## Substituindo dados sinteticos por dados reais

A base sintetica reproduz os fatores de risco da proposta. Para usar dados
reais, basta entregar um CSV com as mesmas colunas usadas em
`modelo_preditivo.py` (`NUMERICAS`, `BINARIAS`, `CATEGORICAS` e `faltou`).
O restante do pipeline nao muda.

## Parametros principais

- `--lam`: penalizacao por atraso esperado (secao 10.8). Maior = agenda mais
  conservadora; menor = agenda mais agressiva em ocupacao.
- `--orcamento`: limite de custo das confirmacoes ativas por dia (secao 11).
- Capacidade e overbooking por horario/modalidade: `montar_capacidades` em
  `src/pipeline.py`.

## Privacidade (secao 16)

A base usa identificadores anonimizados. Em producao, manter pseudonimizacao,
acesso restrito e conformidade com a LGPD. O score e ferramenta de apoio a
decisao, nunca mecanismo de exclusao de pacientes.

## Documentacao (leigos e gestores)

Material completo em linguagem acessivel — comece pelo [indice](docs/INDICE.md):

| Documento | Conteudo |
|---|---|
| [docs/GUIA_COMPLETO.md](docs/GUIA_COMPLETO.md) | Explicacao integral do app (ideia ao treino do modelo) |
| [docs/01_IDEA_E_OBJETIVO.md](docs/01_IDEA_E_OBJETIVO.md) | Problema, solucao e objetivo do MVP |
| [docs/02_COMO_FUNCIONA_PASSO_A_PASSO.md](docs/02_COMO_FUNCIONA_PASSO_A_PASSO.md) | Fluxo do dado a agenda final |
| [docs/03_COMO_O_MODELO_APRENDE.md](docs/03_COMO_O_MODELO_APRENDE.md) | Treinamento e avaliacao do modelo preditivo |
| [docs/04_GUIA_DA_INTERFACE.md](docs/04_GUIA_DA_INTERFACE.md) | Abas, sliders e roteiro de demo |
| [docs/05_GLOSSARIO.md](docs/05_GLOSSARIO.md) | Termos tecnicos explicados |
| [docs/06_PERGUNTAS_FREQUENTES.md](docs/06_PERGUNTAS_FREQUENTES.md) | FAQ |
| [docs/07_ETICA_E_PRIVACIDADE.md](docs/07_ETICA_E_PRIVACIDADE.md) | LGPD e uso responsavel |
| [GUIA_EXPLICACAO_APP.md](GUIA_EXPLICACAO_APP.md) | Roteiro para apresentacao a stakeholders |
