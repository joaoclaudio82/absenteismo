# Guia completo do app — Redução de Absenteísmo (CPDI)

Este documento explica **tudo** sobre o aplicativo: a ideia central, como funciona por dentro, como o modelo aprende, o que cada tela mostra e o que significa na prática para uma clínica de diagnóstico por imagem.

> **Público:** gestores, equipe de recepção, profissionais de saúde e qualquer pessoa sem formação em programação ou estatística.

---

## Sumário

1. [A ideia em uma frase](#1-a-ideia-em-uma-frase)
2. [O problema que motivou o app](#2-o-problema-que-motivou-o-app)
3. [A solução proposta: três camadas](#3-a-solução-proposta-três-camadas)
4. [De onde vêm os dados](#4-de-onde-vêm-os-dados)
5. [Como o modelo preditivo funciona e é treinado](#5-como-o-modelo-preditivo-funciona-e-é-treinado)
6. [Classificação de risco e ações recomendadas](#6-classificação-de-risco-e-ações-recomendadas)
7. [Priorização de confirmações (quem ligar?)](#7-priorização-de-confirmações-quem-ligar)
8. [Otimização da agenda (onde encaixar cada paciente?)](#8-otimização-da-agenda-onde-encaixar-cada-paciente)
9. [A interface gráfica (Streamlit)](#9-a-interface-gráfica-streamlit)
10. [Parâmetros da barra lateral](#10-parâmetros-da-barra-lateral)
11. [Indicadores que o app mostra](#11-indicadores-que-o-app-mostra)
12. [Limitações do MVP](#12-limitações-do-mvp)
13. [Ética, privacidade e uso responsável](#13-ética-privacidade-e-uso-responsável)
14. [Próximos passos para uso real](#14-próximos-passos-para-uso-real)

Documentos complementares (leitura por tema):

- [Ideia e objetivo](01_IDEA_E_OBJETIVO.md)
- [Como funciona passo a passo](02_COMO_FUNCIONA_PASSO_A_PASSO.md)
- [Como o modelo aprende](03_COMO_O_MODELO_APRENDE.md)
- [Guia da interface](04_GUIA_DA_INTERFACE.md)
- [Glossário](05_GLOSSARIO.md)
- [Perguntas frequentes](06_PERGUNTAS_FREQUENTES.md)
- [Ética e privacidade](07_ETICA_E_PRIVACIDADE.md)

---

## 1. A ideia em uma frase

O app **prevê quem tem mais chance de faltar**, **decide quem merece uma ligação ou confirmação reforçada** (dentro de um orçamento) e **organiza a agenda do dia** de forma inteligente — equilibrando receita, capacidade dos equipamentos e risco de atraso.

Não substitui a equipe humana. **Apoia a decisão** com dados.

---

## 2. O problema que motivou o app

### O que é absenteísmo?

**Absenteísmo** é quando o paciente **não comparece** ao exame agendado, sem avisar com antecedência suficiente (no-show). Também inclui cancelamentos em cima da hora que deixam a vaga ociosa.

### Por que isso importa?

Em uma clínica de imagem (ultrassom, tomografia, ressonância, etc.):

| Consequência | Impacto |
|---|---|
| Equipamento parado | Custo fixo alto (RM, TC) sem gerar receita |
| Vaga desperdiçada | Paciente da fila de espera não entra |
| Agenda mal planejada | Atrasos em cascata no restante do dia |
| Confirmações genéricas | Liga para todo mundo ou para ninguém — ineficiente |

### O que a clínica faz hoje (em geral)

- Envia lembrete igual para todos.
- Confirma manualmente por ordem de chegada na lista.
- Monta a agenda sem considerar **probabilidade de falta**.
- Não sabe **onde** gastar o esforço de ligação para ter melhor retorno.

### O que o app propõe

Tratar cada agendamento de forma **diferenciada**, com base em evidências:

1. Quem tem **baixo risco** → lembrete simples.
2. Quem tem **alto risco** → ligação ativa, reforço de preparo.
3. A **agenda** considera que alguns pacientes provavelmente não virão → melhor uso de overbooking e horários.

---

## 3. A solução proposta: três camadas

O app implementa uma proposta acadêmica (CPDI) em três etapas encadeadas:

```
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 1 — PREDITIVA                                       │
│  Entrada: dados do agendamento (idade, histórico, turno…)   │
│  Saída:   probabilidade de falta (ex.: 42%)                   │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 2 — DECISÓRIA                                       │
│  • Classifica em faixa de risco (baixo → muito alto)        │
│  • Define ação recomendada por faixa                        │
│  • Escolhe QUEM recebe confirmação ativa (com orçamento)    │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 3 — OTIMIZAÇÃO                                      │
│  Aloca cada paciente em horário × modalidade                │
│  Maximiza receita esperada, controla atraso e capacidade   │
└─────────────────────────────────────────────────────────────┘
```

**Analogia simples:** imagine um hospital que recebe 120 pacientes amanhã.

- **Camada 1** = meteorologista: "40% de chance de chuva (falta) para este paciente".
- **Camada 2** = gerente de operações: "Leve guarda-chuva (SMS) ou mande equipe (ligação)?".
- **Camada 3** = planejador de tráfego: "Como distribuir os carros nas faixas sem engarrafar?".

---

## 4. De onde vêm os dados

### No MVP (versão atual)

O app usa uma **base sintética** — dados gerados por computador que imitam uma clínica real. Arquivo: `data/agendamentos.csv`.

Por quê sintético? Para demonstrar o sistema **sem expor dados reais de pacientes**. A estrutura é a mesma que a clínica usaria depois.

### O que cada registro contém

Cada linha é um **agendamento** com informações como:

| Grupo | Exemplos de campos |
|---|---|
| Paciente | idade, distância até a clínica, se é paciente novo |
| Histórico | faltas anteriores, comparecimentos anteriores |
| Exame | modalidade (US, TC, RM…), duração, receita estimada |
| Agendamento | canal (WhatsApp, telefone…), convênio, turno, antecedência |
| Contato | se já confirmou, quantas tentativas de contato |
| Resultado | `faltou` (0 = compareceu, 1 = faltou) — usado no treino |

### Taxa de absenteísmo simulada

A base sintética reproduz padrões conhecidos da literatura e da proposta:

- Quem **não confirmou** falta mais.
- Quem tem **faltas anteriores** falta mais.
- **Turno da noite** e **paciente novo** aumentam risco.
- **Agendamento presencial** reduz risco.
- Exames com **preparo complexo** aumentam risco.

A taxa média fica em torno de **15–25%** (varia conforme a geração).

### Migrando para dados reais

Basta substituir o CSV por dados históricos anonimizados da clínica, mantendo as mesmas colunas. O restante do app continua igual.

---

## 5. Como o modelo preditivo funciona e é treinado

Esta é a parte mais técnica — explicada em linguagem acessível. Detalhes extras em [03_COMO_O_MODELO_APRENDE.md](03_COMO_O_MODELO_APRENDE.md).

### O que o modelo faz

Para cada agendamento **novo** (de hoje), o modelo responde:

> "Qual a probabilidade deste paciente **não comparecer**?"

Exemplo: `prob_falta = 0,42` → 42% de chance de falta.

### O que significa "treinar" um modelo

**Treinar** = o computador **aprende com o passado**.

1. Pega milhares de agendamentos antigos onde já sabemos o resultado (`faltou` sim ou não).
2. Procura **padrões**: o que os que faltaram tinham em comum?
3. Guarda esses padrões em um arquivo (`data/modelo.joblib`).
4. Depois, para agendamentos novos, aplica os padrões aprendidos.

**Analogia:** como um médico experiente que, depois de ver mil casos, intui "este perfil costuma faltar" — só que o modelo faz isso com matemática e em escala.

### Dois modelos treinados (por quê dois?)

| Modelo | Papel | Usado onde |
|---|---|---|
| **Regressão logística** | Simples, interpretável — mostra *quais fatores* aumentam ou reduzem risco | Aba Visão geral (gráfico de fatores) |
| **Gradient boosting calibrado** | Mais preciso, captura relações complexas | Decisões operacionais (risco, confirmações, agenda) |

### Passo a passo do treinamento (o que acontece no código)

1. **Separação dos dados**
   - 75% para **treino** (aprender)
   - 25% para **teste** (avaliar se aprendeu de verdade, sem "cola")

2. **Pré-processamento**
   - Números (idade, distância) são normalizados para mesma escala.
   - Categorias (convênio, modalidade) viram colunas binárias (one-hot encoding).

3. **Treino da regressão logística**
   - Modelo clássico de estatística.
   - `class_weight="balanced"` — dá mais peso a faltas porque são menos frequentes que comparecimentos.

4. **Treino do gradient boosting + calibração**
   - Gradient boosting: combina muitas árvores de decisão pequenas.
   - **Calibração isotônica:** ajusta as probabilidades para serem **confiáveis** (se o modelo diz 30%, ~30% realmente faltam). Essencial porque a agenda usa o número diretamente.

5. **Avaliação**
   - **AUC-ROC** (~0,73 no MVP): quão bem separa quem falta de quem comparece. Escala 0,5 (chute) a 1,0 (perfeito).
   - **Brier score** (~0,20): qualidade das probabilidades. Quanto **menor**, melhor.

6. **Persistência**
   - Modelo salvo em `data/modelo.joblib`.
   - Na interface, treina **só na primeira vez**; depois carrega o arquivo salvo.

### Variáveis que o modelo usa

**Numéricas:** idade, faltas anteriores, comparecimentos anteriores, distância (km), duração do exame, receita estimada, antecedência (dias), tentativas de contato.

**Sim/não:** paciente novo, necessita preparo, usa contraste, já confirmou.

**Categorias:** modalidade, canal de agendamento, convênio, turno, dia da semana.

### O que o modelo NÃO faz

- Não usa nome, CPF ou endereço.
- Não "pune" pacientes — só estima probabilidade.
- Não decide sozinho cancelar agendamento (isso é política da clínica).

---

## 6. Classificação de risco e ações recomendadas

Depois de calcular `prob_falta`, o app classifica cada paciente em uma **faixa** (Tabela 1 da proposta):

| Probabilidade | Nível | Ação recomendada |
|---|---|---|
| 0% a 15% | **Baixo** | Lembrete automático simples (WhatsApp/SMS) |
| 15% a 35% | **Médio** | Mensagem reforçada pedindo confirmação |
| 35% a 60% | **Alto** | Ligação ativa + reforço de preparo + confirmação obrigatória |
| 60% ou mais | **Muito alto** | Confirmação obrigatória; libera vaga se não responder; aciona lista de espera |

Isso transforma um número abstrato (0,42) em **protocolo operacional** que a recepção entende.

---

## 7. Priorização de confirmações (quem ligar?)

### O dilema

A clínica não pode ligar para **todos** os 120 pacientes do dia. Tempo e dinheiro são limitados.

### A pergunta que o app responde

> Com **R$ 200** para ligações hoje, **para quais pacientes** devo ligar para **maximizar o retorno**?

### Como decide (em linguagem simples)

Para cada paciente, calcula:

```
Ganho = (Receita do exame) × (Quanto a ligação reduz o risco) − (Custo da ligação)
```

Exemplo numérico:

- Receita: R$ 950 (ressonância)
- Risco atual: 50%
- Ligação reduz 40% do risco → risco cai para 30%
- Receita "salva": 950 × (0,50 − 0,30) = R$ 190
- Custo da ligação: R$ 4
- **Ganho líquido: R$ 186** → vale a pena ligar!

Para um exame barato (R$ 90) com risco baixo (15%), o ganho pode ser **negativo** → não liga.

O algoritmo seleciona o conjunto de pacientes que **maximiza o ganho total**, sem ultrapassar o orçamento. Isso é o clássico **problema da mochila** da matemática.

### Parâmetros que você controla

- **Orçamento diário** — teto de gasto.
- **Custo por intervenção** — quanto custa uma ligação.
- **Redução de risco** — eficácia estimada da ligação.

---

## 8. Otimização da agenda (onde encaixar cada paciente?)

### O dilema

Cada paciente precisa de um **horário** e um **equipamento** (modalidade). Os equipamentos têm **capacidade limitada** por hora. Alguns pacientes provavelmente **não virão** — dá para agendar um pouco a mais (overbooking), mas demais gera atraso.

### O que o otimizador faz

Distribui os pacientes do dia nos slots de horário (08:00, 09:00… 16:00) × modalidade, buscando:

- **Maximizar receita esperada** (considerando probabilidade de comparecimento)
- **Minimizar atraso esperado** (penalizado pelo parâmetro Lambda)

### Regras que respeita

1. Cada paciente vai para **no máximo um** horário.
2. Só aloca em equipamento **compatível** (RM com RM, US com US).
3. **Capacidade:** soma das durações esperadas (ajustada pelo risco) não pode exceder o limite do bloco.
4. **Overbooking:** pode agendar um pouco além da capacidade nominal, até um limite.
5. **Atraso:** se a ocupação esperada passa da capacidade, conta como atraso e é penalizada.

### Parâmetro Lambda (λ)

Controla o **trade-off**:

| Lambda | Comportamento |
|---|---|
| **Alto** (ex.: 10) | Agenda conservadora — menos lotada, menos atraso, pode deixar receita na mesa |
| **Baixo** (ex.: 0,5) | Agenda agressiva — mais pacientes, mais receita potencial, mais risco de atraso |
| **Padrão** (2,0) | Equilíbrio intermediário |

---

## 9. A interface gráfica (Streamlit)

O app roda no navegador (`http://localhost:8501`). Quatro abas:

### Aba 📊 Visão geral

Painel executivo do dia:

- Taxa histórica de absenteísmo na base completa.
- Receita potencial do dia simulado.
- Perda esperada por faltas.
- Desempenho dos modelos (AUC-ROC, Brier).
- Gráfico dos principais fatores de risco.

**Para quem:** diretoria, gestores — visão rápida do impacto.

### Aba 🎯 Risco

Detalhamento da escoragem:

- Gráfico de barras por faixa de risco.
- Histograma de probabilidades.
- Tabela de ações por faixa.
- Lista filtrável de agendamentos (ex.: só alto e muito alto).

**Para quem:** coordenação de enfermagem, recepção — quem precisa de atenção especial.

### Aba 📞 Confirmações

Priorização sob orçamento:

- Quantas intervenções foram selecionadas.
- Ganho esperado e custo total.
- Gráfico dispersão risco × receita (vermelho = ligar).
- Lista de quem recebe intervenção, ordenada por ganho.

**Para quem:** call center, recepção — lista de trabalho do dia.

### Aba 🗓️ Agenda

Otimização de alocação:

- Status do solver, pacientes alocados.
- Receita esperada e atraso total.
- Mapa de calor ocupação × horário × modalidade.
- Tabela de alocações detalhadas.

**Para quem:** gestão de agenda, supervisores de modalidade.

Guia detalhado da interface: [04_GUIA_DA_INTERFACE.md](04_GUIA_DA_INTERFACE.md).

---

## 10. Parâmetros da barra lateral

Todos ficam na **sidebar esquerda** e atualizam o app em tempo real (sem retreinar o modelo).

| Parâmetro | Faixa | Padrão | Efeito |
|---|---|---|---|
| Agendamentos do dia | 40–400 | 120 | Tamanho do "dia" simulado |
| Orçamento diário (R$) | 50–600 | 200 | Teto de gasto com ligações |
| Custo por intervenção (R$) | 1–15 | 4 | Custo unitário de cada ligação |
| Redução de risco da ação | 0,1–0,7 | 0,4 | Eficácia da intervenção (40%) |
| Capacidade/bloco (min) | 30–120 | 60 | Minutos disponíveis por slot |
| Overbooking/bloco (min) | 0–60 | 20 | Margem extra além da capacidade |
| Lambda | 0–15 | 2 | Peso da penalidade por atraso |

---

## 11. Indicadores que o app mostra

| Indicador | Significado |
|---|---|
| Taxa de absenteísmo (base) | % histórico de faltas em toda a base de dados |
| Receita potencial do dia | Soma da receita de todos os agendamentos simulados |
| Perda esperada por faltas | Quanto se espera perder: Σ (receita × prob_falta) |
| AUC-ROC | Qualidade discriminativa do modelo (0,5 a 1,0) |
| Brier score | Qualidade das probabilidades (menor = melhor) |
| Intervenções selecionadas | Quantos pacientes recebem ligação ativa |
| Ganho esperado líquido | Retorno financeiro estimado das ligações |
| Pacientes alocados | Quantos foram encaixados na agenda otimizada |
| Atraso esperado | Minutos totais de atraso estimados na agenda |

---

## 12. Limitações do MVP

Seja transparente ao apresentar:

1. **Dados sintéticos** — números mudam com base real.
2. **Parâmetros calibráveis** — custo de ligação, eficácia, capacidade precisam ser ajustados com a operação.
3. **Simulação de um dia** — pega os primeiros N registros do CSV, não um dia calendário real.
4. **Sem integração** — não conecta ao sistema de agendamento da clínica (ainda).
5. **Overbooking** — decisão de política clínica; o app quantifica, não impõe.

---

## 13. Ética, privacidade e uso responsável

- Dados anonimizados; sem nomes ou documentos.
- Score é **ferramenta de apoio**, nunca critério de exclusão.
- Conformidade com LGPD em produção.
- Detalhes: [07_ETICA_E_PRIVACIDADE.md](07_ETICA_E_PRIVACIDADE.md).

---

## 14. Próximos passos para uso real

1. Substituir base sintética por histórico real anonimizado.
2. Calibrar custos e eficácia das intervenções com dados da clínica.
3. Integrar exportação diária com o sistema de agendamento.
4. Medir impacto: comparecimento e receita antes/depois.
5. Retreinar o modelo periodicamente (ex.: trimestral).

---

## Como executar o app

```bash
cd mvp_absenteismo
pip install -r requirements.txt
python -m streamlit run app.py
```

Abra `http://localhost:8501` no navegador.

---

*Documento gerado para o MVP CPDI — Estratégia Inteligente para Redução do Absenteísmo.*
