# Glossário

Termos usados no app e na documentação, explicados para quem não é da área técnica.

---

## A

**Absenteísmo / No-show**  
Quando o paciente não comparece ao exame agendado, especialmente sem aviso prévio suficiente. Gera perda de receita e ociosidade de equipamentos.

**AUC-ROC**  
Medida de qualidade do modelo preditivo (0,5 a 1,0). Indica quão bem o modelo **distingue** quem falta de quem comparece. Quanto mais perto de 1, melhor. 0,5 = chute aleatório.

**Antecedência (dias)**  
Quantos dias se passaram entre a **marcação** do exame e a **data** do exame. Marcações muito antecipadas podem aumentar risco de falta.

---

## B

**Brier score**  
Medida de qualidade das **probabilidades** previstas (0 a 1). Quanto **menor**, melhor. Penaliza modelos que dizem 90% mas acertam pouco.

**Boosting / Gradient boosting**  
Técnica de machine learning que combina muitos modelos simples (árvores) em sequência. Cada um corrige erros do anterior. Usado no app para predição operacional.

**Base sintética**  
Dados gerados por computador que imitam uma clínica real. Usada no MVP para demonstração sem expor dados de pacientes.

---

## C

**Calibração (isotônica)**  
Ajuste que torna as probabilidades do modelo **confiáveis**. Se o modelo diz 30%, aproximadamente 30% dos casos similares realmente faltam.

**Camada decisória**  
Segunda etapa do app: transforma probabilidades em faixas de risco, ações e priorização de ligações.

**Camada preditiva**  
Primeira etapa: estima probabilidade de falta para cada agendamento.

**Camada de otimização**  
Terceira etapa: aloca pacientes em horários e modalidades maximizando receita e controlando atraso.

**Capacidade (por bloco)**  
Minutos disponíveis em um horário para uma modalidade. Ex.: 60 min no RM das 09:00.

**CPDI**  
Contexto acadêmico em que a proposta de redução de absenteísmo foi desenvolvida.

**CSV**  
Formato de arquivo de planilha (texto separado por vírgulas). O app lê `data/agendamentos.csv`.

---

## D

**Desfecho**  
Resultado do agendamento: compareceu, faltou sem aviso, cancelou, remarcou, etc.

---

## F

**Feature / Variável / Característica**  
Cada informação de entrada do modelo: idade, modalidade, se confirmou, etc.

**Faixa de risco**  
Categoria derivada da probabilidade: baixo, médio, alto, muito alto.

---

## G

**Ganho esperado líquido**  
Retorno financeiro estimado das ligações selecionadas: receita salva pelas intervenções menos custo total.

---

## L

**Lambda (λ)**  
Parâmetro que controla o trade-off entre receita e atraso na otimização da agenda. Maior lambda = agenda mais conservadora.

**LGPD**  
Lei Geral de Proteção de Dados. Exige cuidado com dados pessoais; o app usa identificadores anonimizados.

**Log-odds**  
Escala interna usada pela regressão logística antes de converter em probabilidade. Coeficientes positivos aumentam log-odds (e risco).

---

## M

**Machine learning / Aprendizado de máquina**  
Técnicas em que o computador aprende padrões a partir de dados, sem regras fixas programadas manualmente.

**Modalidade**  
Tipo de exame: ultrassonografia, tomografia, ressonância, radiografia, mamografia, densitometria.

**MVP (Minimum Viable Product)**  
Produto mínimo viável — versão funcional para demonstrar a ideia, não sistema final de produção.

**Mochila (problema da)**  
Problema clássico de otimização: escolher itens com valor e peso (custo), dentro de capacidade limitada (orçamento). Usado para priorizar ligações.

---

## O

**One-hot encoding**  
Conversão de categorias (ex.: convênio) em colunas binárias (sim/não) para o modelo processar.

**Overbooking**  
Agendar além da capacidade nominal, apostando que alguns pacientes faltarão. Controlado por limite em minutos extras.

**Otimização / PLI (Programação Linear Inteira)**  
Técnica matemática para encontrar a **melhor** alocação respeitando regras (capacidade, compatibilidade). Variáveis são 0 ou 1 (aloca ou não).

**Orçamento (de confirmação)**  
Limite de gasto diário com ligações e contatos ativos.

---

## P

**Pipeline**  
Sequência automatizada de etapas: dados → modelo → risco → confirmações → agenda.

**prob_falta**  
Probabilidade estimada de o paciente faltar (valor entre 0 e 1). Ex.: 0,42 = 42%.

**PuLP**  
Biblioteca Python que resolve problemas de otimização (mochila e agenda). Usada nos bastidores do app.

---

## R

**Regressão logística**  
Modelo estatístico clássico para prever probabilidades. Interpretável — mostra peso de cada fator.

**Receita estimada**  
Valor financeiro esperado do exame (R$), conforme modalidade e convênio.

**Retreinar**  
Rodar o aprendizado de novo com dados atualizados. Recomendado periodicamente em produção.

---

## S

**Score / Escoragem**  
Atribuição de probabilidade de falta a cada agendamento pelo modelo.

**Streamlit**  
Ferramenta Python para criar interfaces web interativas. O app roda sobre ela.

---

## T

**Taxa de absenteísmo**  
Percentual de agendamentos em que o paciente faltou. Ex.: 18% = 18 faltas a cada 100 agendamentos.

**Treino / Teste (split)**  
Divisão dos dados: treino para aprender, teste para avaliar sem "cola".

**Turno**  
Período do dia: manhã, tarde ou noite.

---

## Próxima leitura

- [Perguntas frequentes](06_PERGUNTAS_FREQUENTES.md)
- [Guia completo](GUIA_COMPLETO.md)
