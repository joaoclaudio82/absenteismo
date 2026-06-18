# Guia da interface — como usar o app

Instruções para navegar no aplicativo Streamlit, aba por aba e controle por controle.

---

## Como abrir

```bash
cd mvp_absenteismo
python -m streamlit run app.py
```

Abra no navegador: **http://localhost:8501**

Na **primeira execução**, aguarde alguns segundos — o modelo está sendo treinado. Nas próximas, abre quase instantaneamente.

---

## Layout geral

```
┌──────────────────┬────────────────────────────────────────────┐
│                  │  🩺 Estrategia Inteligente...              │
│   SIDEBAR        │  ─────────────────────────────────────     │
│   (parâmetros)   │  [Visão geral] [Risco] [Confirmações] [Agenda] │
│                  │                                            │
│                  │  (conteúdo da aba selecionada)              │
└──────────────────┴────────────────────────────────────────────┘
```

- **Esquerda:** controles que você ajusta
- **Centro:** resultados e gráficos
- **Topo:** quatro abas temáticas

---

## Barra lateral (parâmetros)

### Agendamentos do dia

- **O que é:** quantos pacientes simular no "dia de hoje"
- **Faixa:** 40 a 400 (passos de 20)
- **Padrão:** 120
- **Efeito:** muda todas as abas — mais pacientes = números maiores, mais variabilidade

---

### Confirmacao ativa (sec. 11)

Estes três controles afetam a aba **Confirmações**.

#### Orçamento diario (R$)

- Quanto a clínica pode **gastar hoje** em ligações/mensagens ativas
- Padrão: R$ 200
- **Teste:** suba para R$ 500 → mais pacientes selecionados para ligação

#### Custo por intervencao (R$)

- Quanto **custa** cada ligação ou contato reforçado
- Padrão: R$ 4,00
- **Teste:** suba para R$ 10 → menos ligações cabem no orçamento

#### Reducao de risco da acao

- Quanto a intervenção **reduz** a probabilidade de falta
- Padrão: 0,40 (40%)
- Exemplo: risco 50% → após ligação, 30%
- **Teste:** suba para 0,60 → ligações ficam mais "rentáveis", mais seleções

---

### Agenda (sec. 10)

Estes três controles afetam a aba **Agenda**.

#### Capacidade/bloco (min)

- Minutos **disponíveis** em cada horário por modalidade
- Padrão: 60 min
- **Teste:** reduza para 30 → menos pacientes alocados, mais apertado

#### Overbooking/bloco (min)

- Minutos **extras** que podem ser agendados além da capacidade
- Padrão: 20 min
- Aposta controlada: alguns pacientes faltam, sobra vaga
- **Teste:** zere → agenda mais rígida

#### Lambda (penaliza atraso)

- Peso da **penalidade por atraso** na otimização
- Padrão: 2,0
- **Alto (10+):** agenda conservadora, pouco atraso
- **Baixo (0,5):** agenda agressiva, mais receita, mais atraso
- **Teste:** compare aba Agenda com lambda 0,5 vs. 10

---

## Aba 📊 Visao geral

### Cards no topo

| Card | Significado |
|---|---|
| Taxa de absenteísmo (base) | % de faltas em **toda** a base histórica (~8.000 registros) |
| Receita potencial do dia | Soma da receita dos agendamentos simulados hoje |
| Perda esperada por faltas | Quanto se espera perder: receita × prob_falta de cada um |
| AUC-ROC (boosting) | Qualidade do modelo preditivo |

### Tabela de modelos

Compara regressão logística vs. gradient boosting em AUC-ROC e Brier score.

### Gráfico de fatores de risco

Barras horizontais — **peso** de cada variável na regressão logística.

- Barra para a **direita** (positiva) → aumenta risco de falta
- Barra para a **esquerda** (negativa) → reduz risco

---

## Aba 🎯 Risco

### Gráfico de barras (esquerda)

Quantos agendamentos em cada faixa: baixo, médio, alto, muito alto.

Cores: verde → amarelo → laranja → vermelho.

### Histograma (direita)

Distribuição das probabilidades de falta. Linhas tracejadas = limites das faixas.

### Tabela de ações por faixa

Referência rápida do protocolo recomendado.

### Agendamentos escorados

- Filtro **Filtrar por nivel:** escolha quais faixas ver (padrão: alto + muito alto)
- Colunas: ID, modalidade, turno, convênio, confirmado, prob_falta, nível, ação

**Uso prático:** exporte mentalmente a lista de alto/muito alto para a equipe de confirmação.

---

## Aba 📞 Confirmacoes

### Cards no topo

| Card | Significado |
|---|---|
| Intervenções selecionadas | X de Y pacientes receberão ligação |
| Ganho esperado líquido | Retorno financeiro estimado das ligações |
| Custo total | Quanto será gasto (≤ orçamento) |

### Gráfico de dispersão

- **Eixo X:** probabilidade de falta
- **Eixo Y:** receita estimada
- **Vermelho:** intervir (ligar)
- **Cinza:** não intervir

Pacientes no canto **superior direito** (alto risco + alta receita) são os prioritários.

### Tabela inferior

Lista de quem recebe intervenção, ordenada por ganho unitário (maior primeiro).

---

## Aba 🗓️ Agenda

### Cards no topo

| Card | Significado |
|---|---|
| Status | Optimal = solução encontrada com sucesso |
| Pacientes alocados | Quantos encaixados de quantos total |
| Receita esperada | Receita ajustada pela prob. de comparecimento |
| Atraso esperado | Minutos totais de atraso estimados |

### Mapa de calor

Ocupação esperada (minutos) por **horário** (colunas) × **modalidade** (linhas).

Cores mais quentes = bloco mais cheio.

### Ocupacao detalhada por bloco

Tabela numérica: ocupação esperada, bruta, capacidade e overbooking por slot.

### Alocacoes

Lista final: qual paciente → qual horário → qual modalidade, com prob_falta e nível de risco.

---

## Roteiro de demonstração (5 minutos)

1. Abra com padrões → mostre **Visão geral** (KPIs + fatores de risco).
2. Vá em **Risco** → filtre alto/muito alto.
3. Na sidebar, **dobre o orçamento** → vá em **Confirmações** → mostre mais pontos vermelhos.
4. Na sidebar, **lambda = 10** → vá em **Agenda** → note menos atraso.
5. **Lambda = 0,5** → compare receita vs. atraso.

---

## Problemas comuns

| Situação | O que fazer |
|---|---|
| App demora na 1ª vez | Normal — treinando modelo; aguarde |
| `streamlit` não encontrado | Use `python -m streamlit run app.py` |
| Gráficos vazios | Aumente "Agendamentos do dia" |
| Agenda com poucos alocados | Aumente capacidade ou overbooking |

---

## Próxima leitura

- [Glossário](05_GLOSSARIO.md)
- [Perguntas frequentes](06_PERGUNTAS_FREQUENTES.md)
- [Guia completo](GUIA_COMPLETO.md)
