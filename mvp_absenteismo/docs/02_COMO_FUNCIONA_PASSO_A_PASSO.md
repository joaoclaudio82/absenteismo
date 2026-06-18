# Como o app funciona — passo a passo

Este documento descreve o **fluxo completo**, do dado bruto até a agenda final, como se você estivesse acompanhando um dia de trabalho na clínica.

---

## Visão do fluxo

```
[1] Dados históricos
         ↓
[2] Treino do modelo (uma vez)
         ↓
[3] Escoragem do dia (probabilidade de falta)
         ↓
[4] Classificação por faixa de risco
         ↓
[5] Priorização de confirmações
         ↓
[6] Otimização da agenda
         ↓
[7] Resultados nas abas do app
```

---

## Passo 1 — Dados históricos

**O que acontece:** O app carrega milhares de agendamentos passados de `data/agendamentos.csv`.

**Cada registro tem:** idade, modalidade, convênio, se confirmou, se faltou, etc.

**No MVP:** dados são sintéticos (gerados por computador). Na clínica real, viriam do sistema de agendamento.

---

## Passo 2 — Treino do modelo (primeira execução)

**O que acontece:** O computador analisa o passado e aprende padrões.

**Entrada:** características do agendamento + resultado (`faltou`: sim/não).

**Saída:** arquivo `data/modelo.joblib` com os padrões aprendidos.

**Quando roda:** na **primeira vez** que você abre o app (demora alguns segundos). Depois, carrega o arquivo salvo.

**Analogia:** como estudar para uma prova — feito uma vez, usado muitas vezes.

Detalhes: [Como o modelo aprende](03_COMO_O_MODELO_APRENDE.md).

---

## Passo 3 — Escoragem do dia

**O que acontece:** Para cada agendamento do "dia simulado", o modelo calcula `prob_falta`.

**Exemplo:**

| Paciente | Modalidade | Confirmado? | prob_falta |
|---|---|---|---|
| #1042 | Ressonância | Não | 58% |
| #1043 | Ultrassom | Sim | 12% |
| #1044 | Tomografia | Não | 41% |

**Controle:** slider "Agendamentos do dia" define quantos pacientes entram (40 a 400).

---

## Passo 4 — Classificação por faixa de risco

**O que acontece:** Cada probabilidade vira um **nível** e uma **ação**.

| prob_falta | Nível | Ação |
|---|---|---|
| 12% | Baixo | SMS simples |
| 58% | Alto | Ligação ativa |
| 72% | Muito alto | Confirmação obrigatória |

**Onde ver:** aba **Risco** — gráficos e tabela filtrável.

---

## Passo 5 — Priorização de confirmações

**O que acontece:** Com orçamento limitado (ex.: R$ 200), o app escolhe **para quem vale ligar**.

**Lógica simplificada:**

1. Calcula ganho de cada ligação: receita salva − custo.
2. Descarta quem tem ganho negativo.
3. Seleciona o melhor conjunto que cabe no orçamento.

**Exemplo:** R$ 200 ÷ R$ 4 por ligação ≈ até 50 ligações — mas nem todo mundo tem ganho positivo, então pode ser menos.

**Onde ver:** aba **Confirmações** — gráfico e lista de selecionados.

**Controles:** Orçamento, Custo por intervenção, Redução de risco.

---

## Passo 6 — Otimização da agenda

**O que acontece:** O app distribui pacientes nos horários (08:00–16:00) × modalidades.

**Objetivo:** maximizar receita esperada, penalizando atraso.

**Restrições:**

- RM só no equipamento de RM
- Capacidade de 60 min por bloco (padrão)
- Overbooking de +20 min permitido
- Cada paciente em no máximo 1 slot

**Onde ver:** aba **Agenda** — mapa de calor e tabela de alocações.

**Controles:** Capacidade/bloco, Overbooking/bloco, Lambda.

---

## Passo 7 — Resultados nas abas

| Aba | O que mostra |
|---|---|
| Visão geral | KPIs do dia, desempenho do modelo, fatores de risco |
| Risco | Distribuição por faixa, histograma, lista escorada |
| Confirmações | Quem ligar, ganho esperado, custo |
| Agenda | Onde alocar, ocupação, atraso |

---

## Exemplo concreto (mini-cenário)

**Cenário:** 120 agendamentos, orçamento R$ 200, lambda 2,0.

1. Modelo escora 120 pacientes → média de prob_falta ~22%.
2. 18 em risco alto/muito alto.
3. Confirmações: 47 ligações selecionadas, ganho esperado R$ 3.200, custo R$ 188.
4. Agenda: 115 de 120 alocados, receita esperada R$ 48.000, atraso 45 min.

*(Valores ilustrativos — variam com os dados e parâmetros.)*

---

## O que muda quando você mexe nos sliders

| Você muda | O que acontece |
|---|---|
| Agendamentos do dia ↑ | Mais pacientes no cenário; métricas mudam |
| Orçamento ↑ | Mais ligações possíveis |
| Custo por intervenção ↑ | Menos ligações cabem no orçamento |
| Redução de risco ↑ | Ligações ficam mais "rentáveis" |
| Capacidade ↓ | Menos pacientes cabem na agenda |
| Overbooking ↑ | Mais pacientes por bloco, mais risco de atraso |
| Lambda ↑ | Agenda mais conservadora, menos atraso |

**Importante:** sliders **não retreinam** o modelo. Só mudam a simulação operacional.

---

## Próxima leitura

- [Como o modelo aprende](03_COMO_O_MODELO_APRENDE.md)
- [Guia da interface](04_GUIA_DA_INTERFACE.md)
- [Guia completo](GUIA_COMPLETO.md)
