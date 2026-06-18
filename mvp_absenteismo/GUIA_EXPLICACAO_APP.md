# Guia para explicar o app — Estratégia Inteligente para Redução do Absenteísmo (CPDI)

Roteiro para apresentação, documentação ou conversa com gestores e equipe técnica.

---

## 1. Abertura: qual problema o app resolve

Comece pelo contexto de negócio:

> Em clínicas de diagnóstico por imagem, **absenteísmo** (paciente que não comparece) gera perda de receita, ociosidade de equipamento e fila de espera mal aproveitada. Hoje a agenda costuma ser montada de forma **reativa**: confirma-se todo mundo igual, ou só quem "parece problemático", sem priorizar quem realmente vale a pena ligar nem otimizar horários considerando risco de falta.

O app implementa a proposta CPDI em **três camadas encadeadas**:

1. **Preditiva** — estima a probabilidade de cada paciente faltar.
2. **Decisória** — classifica risco e decide **quem** recebe confirmação ativa, dentro de um orçamento.
3. **Otimização** — monta a **agenda do dia** maximizando receita e controlando atraso/overbooking.

Não é só um dashboard de BI: é um **sistema de apoio à decisão** com modelos matemáticos executáveis.

---

## 2. Visão geral da arquitetura (1 slide ou 1 minuto)

Use este fluxo:

```
Histórico de agendamentos
        ↓
[Modelo preditivo]  →  p_i = probabilidade de falta
        ↓
[Camada decisória]  →  faixa de risco + ação recomendada
        ↓              priorização de confirmações (mochila)
[Otimização agenda] →  alocação horário × modalidade (PLI)
        ↓
Agenda inteligente + lista de quem ligar
```

Enfatize: cada camada **consome a saída da anterior**. A probabilidade mal calibrada prejudica agenda e confirmações — por isso o modelo usa calibração isotônica.

---

## 3. Dados: de onde vêm e o que entram no modelo

### Hoje (MVP)

- Base **sintética** em `data/agendamentos.csv`, gerada por `gerar_dados.py`.
- Simula padrões realistas: histórico de faltas, antecedência, turno, modalidade, canal, convênio, confirmação etc.

### Em produção

- Substituir pelo CSV real da clínica, **mesmas colunas** do modelo:
  - **Numéricas:** idade, faltas anteriores, distância, duração, receita, antecedência…
  - **Binárias:** paciente novo, precisa preparo, usa contraste, já confirmou
  - **Categóricas:** modalidade, canal, convênio, turno, dia da semana
  - **Alvo histórico:** `faltou` (0/1)

Frase importante para gestores:

> O app **não exclui pacientes**. O score orienta **como** tratar cada agendamento (lembrete simples vs. ligação ativa) e **como** montar a agenda — em linha com LGPD e uso ético descrito na proposta.

---

## 4. Camada preditiva (o "cérebro" estatístico)

Explique em duas frases técnicas + uma tradução:

**O que faz:** para cada agendamento, calcula `prob_falta` ∈ [0, 1].

**Como treina:**

- **Regressão logística** — baseline interpretável; os coeficientes aparecem na aba Visão geral (quais fatores aumentam/diminuem risco).
- **Gradient boosting calibrado** — captura relações não lineares; é o modelo usado nas decisões operacionais.

**Métricas exibidas:**

- **AUC-ROC** — capacidade de separar quem falta de quem comparece.
- **Brier score** — qualidade das probabilidades (quanto menor, melhor para o otimizador).

**Detalhe técnico relevante:** o treino roda **uma vez** e fica salvo em `data/modelo.joblib`. A interface só **escora** pacientes novos — por isso os sliders respondem rápido.

---

## 5. Camada decisória — risco (aba **Risco**)

### Classificação por faixas (Tabela 1 da proposta)

| Probabilidade | Nível       | Ação sugerida                                                      |
|---------------|-------------|--------------------------------------------------------------------|
| 0–15%         | Baixo       | Lembrete automático (WhatsApp/SMS)                                 |
| 15–35%        | Médio       | Mensagem reforçada pedindo confirmação                             |
| 35–60%        | Alto        | Ligação ativa + reforço de preparo                                 |
| ≥ 60%         | Muito alto  | Confirmação obrigatória; libera vaga se não responder              |

Explique que isso **operacionaliza** o score: não é só um número, vira **protocolo de atendimento**.

### O que mostrar na demo

- Gráfico de barras por faixa de risco.
- Histograma de probabilidades (onde está a "massa" do risco do dia).
- Tabela filtrável (ex.: só alto e muito alto).

---

## 6. Camada decisória — confirmações (aba **Confirmações**)

Aqui entra a **otimização sob orçamento** (problema da mochila):

> Dado um orçamento diário limitado, **quais pacientes** devem receber intervenção ativa (ligação, contato reforçado) para maximizar o **ganho esperado líquido**?

**Fórmula intuitiva por paciente:**

- Ganho = receita × (redução de risco de falta) − custo da intervenção
- Só entra quem tem ganho líquido positivo
- Respeita o teto de gasto (`Orçamento diário`)

**Parâmetros da sidebar (traduzir para gestão):**

| Parâmetro                    | Significado                                                         |
|------------------------------|---------------------------------------------------------------------|
| Orçamento diário             | Quanto a clínica pode gastar hoje em call center / contato ativo    |
| Custo por intervenção        | Custo médio de uma ligação ou mensagem premium                      |
| Redução de risco da ação     | Eficácia estimada da intervenção (ex.: ligação reduz 40% a chance)  |

**O que mostrar na demo:**

- Scatter risco × receita: pontos vermelhos = "intervir".
- Métricas: quantas intervenções, ganho esperado, custo total.
- Tabela ordenada por ganho unitário.

Mensagem-chave:

> Não ligamos para todo mundo nem só para os mais arriscados — ligamos para quem **combina alto risco com alta receita**, dentro do que o orçamento permite.

---

## 7. Camada de otimização — agenda (aba **Agenda**)

Esta é a parte mais "científica" da proposta (Programação Linear Inteira):

**Objetivo:** alocar cada paciente em um **horário × modalidade** maximizando:

- receita esperada (considerando probabilidade de comparecimento)
- menos penalidade por **atraso esperado** (controlada por **Lambda**)

**Restrições principais:**

- Cada paciente vai para no máximo um slot.
- **Capacidade** por bloco (minutos disponíveis no equipamento).
- **Overbooking** — margem extra além da capacidade nominal (aposta controlada em no-shows).
- Compatibilidade: RM só vai para slot de RM, etc.

**Parâmetros da sidebar:**

| Parâmetro              | Significado                                                              |
|------------------------|--------------------------------------------------------------------------|
| Capacidade/bloco       | Minutos úteis por horário/modalidade                                     |
| Overbooking/bloco      | Quanto a mais pode ser agendado além da capacidade                       |
| Lambda                 | Trade-off receita vs. atraso: maior = conservador; menor = agressivo     |

**O que mostrar na demo:**

- Mapa de calor ocupação por horário × modalidade.
- Pacientes alocados vs. total do dia.
- Receita esperada e atraso total em minutos.

---

## 8. Aba **Visão geral** — resumo executivo

Use esta aba para **não técnicos**:

- Taxa histórica de absenteísmo na base.
- Receita potencial do dia simulado.
- Perda esperada por faltas (receita × probabilidade de falta).
- Desempenho dos modelos.
- Top fatores de risco (gráfico de barras da regressão logística).

Frase de fechamento:

> Em um único painel vemos **quanto estamos perdendo**, **quão confiável é o modelo** e **o que mais explica a falta**.

---

## 9. Parâmetros da barra lateral (sidebar)

Os parâmetros da barra esquerda são os **controles de simulação** do dia. Eles não retreinam o modelo — só mudam quantos pacientes entram no cenário e como a clínica reage a eles.

### Agendamentos do dia (40–400, padrão 120)

Quantos agendamentos da base histórica entram na simulação **de hoje**. O app pega os primeiros *N* registros do CSV, calcula a probabilidade de falta de cada um e usa esse "dia" nas abas Risco, Confirmações e Agenda.

### Confirmação ativa → aba **Confirmações**

Simula a decisão: *"Ligo, mando WhatsApp reforçado… para quem?"* dentro de um orçamento limitado.

### Agenda → aba **Agenda**

Define a **capacidade física** de cada bloco horário × modalidade e como o otimizador equilibra receita vs. atraso.

### O que **não** muda com esses sliders

- O modelo de machine learning (treinado uma vez e salvo em `data/modelo.joblib`)
- A taxa de absenteísmo histórica da base (métrica da aba Visão geral)

---

## 10. Como conectar sidebar → abas (demo ao vivo)

Roteiro de 3 minutos:

1. **Agendamentos do dia** = tamanho do cenário (40–400 pacientes simulados).
2. Aba **Risco** — mostre a distribuição.
3. Ajuste **Orçamento** na sidebar → aba **Confirmações** muda quem é selecionado.
4. Ajuste **Lambda** → aba **Agenda** muda alocação e atraso esperado.
5. Volte à **Visão geral** — receita potencial e perda esperada.

Isso demonstra que é um **simulador de política operacional**, não um relatório estático.

---

## 11. Limitações honestas (credibilidade)

Mencione proativamente:

- Dados são **sintéticos** no MVP; métricas mudam com base real.
- Parâmetros (custo, redução de risco, capacidade) são **hipóteses calibráveis** com a operação.
- O modelo é **apoio à decisão**, não substitui equipe clínica/recepção.
- Overbooking exige governança clínica — o sistema quantifica trade-off, não decide sozinho política de risco.
- Identificadores na base devem ser **pseudonimizados** em produção (LGPD).

---

## 12. Frases prontas por público

**Para diretoria (30 seg):**

> O sistema prevê quem tem mais chance de faltar, prioriza ligações onde o retorno financeiro compensa o custo, e monta a agenda do dia equilibrando receita e atraso — tudo ajustável em tempo real.

**Para operação/recepção:**

> Vocês recebem uma lista priorizada de quem ligar hoje e uma agenda que já considera quem provavelmente não vem, sem tratar todo mundo igual.

**Para TI/dados:**

> Pipeline sklearn com logit + GB calibrado, decisão via PuLP (mochila + PLI), Streamlit como camada de serviço com cache de modelo e escoramento interativo.

**Para academia/comissão CPDI:**

> Implementação fiel às seções 8–11 e 13 da proposta: predição, Tabela 1 de risco, otimização de confirmações e PLI de agenda com indicadores de desempenho.

---

## 13. Estrutura sugerida de apresentação (15–20 min)

| Tempo | Bloco                                      |
|-------|--------------------------------------------|
| 2 min | Problema + proposta em 3 camadas           |
| 2 min | Dados e privacidade                        |
| 3 min | Modelo preditivo + métricas                |
| 3 min | Faixas de risco e ações                    |
| 4 min | Confirmações sob orçamento (demo)          |
| 4 min | Otimização de agenda (demo)                |
| 2 min | Limitações + próximos passos               |

---

## 14. Próximos passos (se perguntarem "e depois?")

1. Trocar base sintética por dados reais anonimizados.
2. Calibrar custo de intervenção e eficácia com histórico de ligações.
3. Integrar com sistema de agendamento (API/export CSV diário).
4. Medir impacto A/B: taxa de comparecimento e receita por slot antes/depois.

---

## Mapeamento com o código

| Seção da proposta              | Módulo / aba                          |
|--------------------------------|---------------------------------------|
| 7. Dados necessários           | `src/gerar_dados.py`                  |
| 8. Modelo preditivo            | `src/modelo_preditivo.py`             |
| 9. Classificação por risco     | `src/decisao.py` — aba Risco          |
| 10. Otimização da agenda       | `src/otimizacao_agenda.py` — aba Agenda |
| 11. Confirmações ativas        | `src/decisao.py` — aba Confirmações   |
| 13. Indicadores de desempenho  | `src/pipeline.py` — aba Visão geral   |
| Interface gráfica              | `app.py`                              |
