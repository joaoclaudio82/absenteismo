# Como o modelo aprende a prever faltas

Explicação detalhada — mas em linguagem acessível — de como o app treina o modelo de machine learning.

---

## O que é "machine learning" aqui?

**Aprendizado de máquina** = o computador encontra padrões em dados históricos sem ser programado regra por regra.

Em vez de escrever: *"se não confirmou, falta"*, o modelo **descobre** quanto cada fator pesa, sozinho, a partir de milhares de exemplos.

---

## O que queremos prever?

Para cada agendamento, queremos um número entre 0 e 1:

```
prob_falta = probabilidade de o paciente NÃO comparecer
```

- 0,05 → 5% de chance de falta (muito confiável)
- 0,50 → 50% (incerto)
- 0,80 → 80% de chance de falta (muito arriscado)

---

## Com o que o modelo aprende?

### Dados de entrada (features)

Informações disponíveis **no momento do agendamento** (antes de saber se faltou):

**Números:**
- Idade
- Faltas anteriores do paciente
- Comparecimentos anteriores
- Distância até a clínica (km)
- Duração do exame (minutos)
- Receita estimada (R$)
- Antecedência (dias entre marcação e exame)
- Tentativas de contato anteriores

**Sim ou não (0/1):**
- É paciente novo?
- Exame precisa de preparo?
- Usa contraste?
- Já confirmou o horário?

**Categorias:**
- Modalidade (US, TC, RM…)
- Canal (WhatsApp, telefone, site…)
- Convênio
- Turno (manhã, tarde, noite)
- Dia da semana

### O que queremos acertar (alvo)

- `faltou = 1` → paciente faltou
- `faltou = 0` → paciente compareceu

---

## Como funciona o treinamento (passo a passo)

### 1. Separar treino e teste

Dos ~8.000 agendamentos:

- **75% treino** (~6.000) — o modelo **aprende** com estes
- **25% teste** (~2.000) — o modelo **nunca viu** estes durante o aprendizado; servem para avaliar se generalizou

**Por quê separar?** Evitar "cola". Se avaliássemos nos mesmos dados do treino, o modelo pareceria perfeito mas falharia em dados novos.

### 2. Pré-processar os dados

Antes de aprender, os dados são preparados:

| Tipo | Tratamento |
|---|---|
| Números (idade, distância…) | Normalizados (mesma escala) |
| Sim/não | Mantidos como 0 ou 1 |
| Categorias (convênio, modalidade…) | Convertidos em colunas binárias (one-hot) |

Exemplo: convênio "SUS" vira coluna `convenio_sus = 1`, demais convênios = 0.

### 3. Treinar a regressão logística

Modelo estatístico clássico, **interpretável**.

**O que faz:** combina todos os fatores em uma equação que produz probabilidade.

**Vantagem:** podemos ver **coeficientes** — quais variáveis aumentam ou reduzem risco. Aparecem no gráfico da aba Visão geral.

**Exemplo de interpretação:**
- Coeficiente positivo em `faltas_previas` → mais faltas no passado = mais risco hoje
- Coeficiente negativo em `confirmado` → quem confirmou = menos risco

**Ajuste:** `class_weight="balanced"` — dá mais importância a faltas porque são menos frequentes que comparecimentos (evita modelo que sempre diz "vai comparecer").

### 4. Treinar o gradient boosting calibrado

Modelo mais **sofisticado**, usado nas decisões operacionais.

**Gradient boosting:** constrói centenas de "árvores de decisão" pequenas em sequência. Cada árvore corrige os erros da anterior.

**Analogia:** vários especialistas em série, cada um refinando a opinião do anterior.

**Calibração isotônica:** ajuste final para que as probabilidades sejam **honestas**.

| Sem calibração | Com calibração |
|---|---|
| Modelo diz 30%, mas 45% faltam | Modelo diz 30%, ~30% faltam |
| Otimizador de agenda recebe números errados | Decisões mais confiáveis |

**Por quê calibrar?** A agenda usa `prob_falta` diretamente nos cálculos de receita e ocupação. Probabilidade errada = agenda errada.

### 5. Avaliar qualidade

Dois números principais (aba Visão geral):

#### AUC-ROC (Area Under the Curve — Receiver Operating Characteristic)

Mede: **quão bem o modelo separa** quem falta de quem comparece.

| Valor | Interpretação |
|---|---|
| 0,50 | Chute aleatório (inútil) |
| 0,70 | Razoável para problemas reais |
| 0,80+ | Bom |
| 1,00 | Perfeito (raro na prática) |

**No MVP:** ~0,73 (logística) e ~0,73 (boosting).

#### Brier score

Mede: **qualidade das probabilidades** (não só acerto sim/não).

| Valor | Interpretação |
|---|---|
| 0,00 | Perfeito |
| 0,25 | Chute aleatório |
| Menor | Melhor |

**No MVP:** ~0,20.

### 6. Salvar o modelo

Pacote salvo em `data/modelo.joblib` contém:

- Modelo de regressão logística (para interpretação)
- Modelo gradient boosting calibrado (para predição)
- Métricas de avaliação
- Coeficientes da logística

**Na interface:** carrega este arquivo. Treina de novo só se o arquivo não existir.

---

## O que o modelo aprendeu (padrões típicos)

Com base nos coeficientes e na geração sintética, fatores que **aumentam** risco:

- Não confirmou o horário
- Faltas anteriores
- Paciente novo
- Turno da noite
- Exame com preparo complexo
- Agendamento por telefone (vs. presencial)
- Convênio SUS
- Maior distância até a clínica
- Maior antecedência (marcou muito antes)

Fatores que **reduzem** risco:

- Já confirmou
- Histórico de comparecimentos
- Agendamento presencial
- Idade mais avançada (leve efeito)

*Com dados reais da clínica, estes padrões podem diferir.*

---

## Perguntas comuns sobre o modelo

### O modelo "sabe" quem vai faltar com certeza?

**Não.** Dá probabilidades, não certezas. 60% de risco ainda significa 40% de chance de comparecer.

### Por que dois modelos?

- **Logística:** explica *por quê* (interpretabilidade para gestores)
- **Boosting:** prediz *melhor* (precisão para operação)

### O modelo discrimina pacientes?

Usa apenas dados operacionais do agendamento, não raça, religião ou condição clínica. O score orienta **tipo de contato**, não exclusão.

### Com que frequência retreinar?

Recomendado: **trimestral** ou quando houver mudança operacional (novo convênio, novo canal de agendamento, pandemia, etc.).

---

## Próxima leitura

- [Glossário](05_GLOSSARIO.md) — definições de AUC-ROC, Brier, calibração…
- [Perguntas frequentes](06_PERGUNTAS_FREQUENTES.md)
- [Guia completo](GUIA_COMPLETO.md)
