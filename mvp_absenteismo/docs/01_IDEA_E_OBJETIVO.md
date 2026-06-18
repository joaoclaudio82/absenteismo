# Ideia e objetivo do app

## Em uma frase

Prever faltas, priorizar confirmações e organizar a agenda — com inteligência, não no achismo.

---

## O cenário

Imagine uma clínica de diagnóstico por imagem com:

- 6 modalidades (ultrassom, tomografia, ressonância, raio-X, mamografia, densitometria)
- Dezenas ou centenas de agendamentos por dia
- Equipamentos caros que não podem ficar ociosos
- Equipe de recepção limitada para confirmar horários

Todo dia, uma parcela dos pacientes **simplesmente não aparece**. A vaga fica vazia. O equipamento para. A receita some.

Isso é o **absenteísmo** (no-show).

---

## Por que o problema é difícil

Não dá para tratar todo mundo igual:

| Abordagem ingênua | Problema |
|---|---|
| Ligar para todos | Caro, lento, equipe sobrecarregada |
| Não ligar para ninguém | Perde receita em exames de alto valor |
| Ligar só "quando sobra tempo" | Quem mais precisa fica de fora |
| Agendar sem considerar risco | Equipamento ocioso ou fila atrasada |

A solução precisa ser **inteligente e proporcional ao risco e ao valor** de cada agendamento.

---

## A ideia central

O app propõe uma **estratégia em três movimentos**:

### 1. Prever (camada preditiva)

Antes do dia do exame, estimar a **probabilidade de falta** de cada paciente com base em histórico e características do agendamento.

> *"Este agendamento tem 47% de chance de no-show."*

### 2. Decidir (camada decisória)

Transformar essa probabilidade em **ações concretas**:

- Faixa de risco → protocolo (SMS, ligação, confirmação obrigatória)
- Orçamento limitado → **quem** recebe ligação ativa hoje

> *"Ligue para estes 38 pacientes — é onde o retorno compensa o custo."*

### 3. Otimizar (camada de agenda)

Montar a **agenda do dia** considerando:

- Capacidade de cada equipamento por horário
- Probabilidade de comparecimento (não conta com quem provavelmente falta)
- Trade-off entre receita e atraso

> *"Encaixe estes pacientes nestes horários para maximizar receita sem engarrafar."*

---

## Objetivo do MVP

Este projeto é um **MVP** (Minimum Viable Product — produto mínimo viável):

- Demonstrar que a proposta acadêmica **funciona de ponta a ponta**
- Permitir **simular** políticas (orçamento, capacidade, lambda) em tempo real
- Servir de base para integração futura com dados reais da clínica

**Não é** um sistema de produção pronto — é uma **prova de conceito executável**.

---

## O que o app NÃO é

| Não é | Por quê |
|---|---|
| Prontuário eletrônico | Não armazena histórico clínico |
| Sistema de agendamento | Não marca consultas diretamente |
| Ferramenta de exclusão | Não cancela pacientes automaticamente |
| Substituto da equipe | Apoia decisão humana, não a substitui |

---

## Benefícios esperados (quando em produção)

- **Redução de absenteísmo** por confirmações direcionadas
- **Melhor uso de equipamentos** por agenda otimizada
- **Menos esforço desperdiçado** da recepção (liga quem importa)
- **Visibilidade gerencial** — quanto se perde, onde está o risco
- **Decisões baseadas em dados**, não em intuição isolada

---

## Relação com a proposta CPDI

O app implementa a proposta *"Estratégia Inteligente para Redução do Absenteísmo"* desenvolvida no contexto acadêmico CPDI. Cada módulo do código corresponde a uma seção da proposta original (dados, modelo, risco, agenda, confirmações, indicadores).

---

## Próxima leitura

- [Como funciona passo a passo](02_COMO_FUNCIONA_PASSO_A_PASSO.md)
- [Guia completo](GUIA_COMPLETO.md)
