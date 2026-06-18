# Perguntas frequentes (FAQ)

Respostas para dúvidas comuns de gestores, recepção e visitantes do app.

---

## Sobre o app em geral

### Para que serve este app?

Ajuda clínicas de diagnóstico por imagem a **reduzir absenteísmo** prevendo faltas, priorizando confirmações e otimizando a agenda — com base em dados, não no achismo.

### Preciso saber programar para usar?

**Não.** A interface é visual, no navegador. Basta abrir o link local e explorar as abas e sliders.

### Os dados são reais de pacientes?

**No MVP, não.** São dados **sintéticos** (simulados). Em produção, usaria histórico real **anonimizado** da clínica.

### O app substitui a recepção?

**Não.** É ferramenta de **apoio à decisão**. A equipe continua responsável por ligar, confirmar e atender pacientes.

### O app cancela agendamentos automaticamente?

**Não.** Sugere ações (ligar, reforçar confirmação). Cancelar ou remarcar é decisão humana e política da clínica.

---

## Sobre predição e modelo

### O modelo acerta sempre?

**Não.** Dá **probabilidades**, não certezas. Um paciente com 70% de risco ainda pode comparecer.

### Por que 42% e não "vai faltar" ou "não vai faltar"?

Probabilidades permitem **decisões graduadas**: SMS para 10%, ligação para 50%, confirmação obrigatória para 70%. Binário (sim/não) perderia nuance.

### O que é AUC-ROC e devo me preocupar com o número?

Mede qualidade do modelo (0,5 a 1,0). No MVP ~0,73 = **razoável** para dados simulados. Com dados reais, reavalie; ab abaixo de 0,65, investigue.

### Por que treina dois modelos?

Logística **explica** fatores (gráfico na Visão geral). Boosting **prediz melhor** (usado nas decisões). Dois papéis complementares.

### Quanto tempo demora o treino?

Alguns segundos na primeira abertura. Depois, carrega modelo salvo — instantâneo.

### Posso retreinar com dados novos?

Sim, via linha de comando (`python -m src.modelo_preditivo`) ou apagando `data/modelo.joblib` e reabrindo o app.

---

## Sobre risco e confirmações

### O que significa "muito alto" risco?

Probabilidade de falta ≥ 60%. Protocolo sugere confirmação obrigatória e acionar lista de espera se não responder.

### Por que não ligar para todos os de risco alto?

**Orçamento e tempo.** O app escolhe quem maximiza retorno: alto risco **e** alta receita, dentro do limite de gasto.

### De onde vem o "ganho esperado"?

Estimativa: quanto de receita se **salva** reduzindo a probabilidade de falta, menos o **custo** da ligação.

### O que é "redução de risco da ação"?

Suposição de eficácia: a ligação reduz X% da probabilidade de falta. Padrão 40%. Calibrável com histórico real da clínica.

### E se eu não souber o custo de uma ligação?

Use estimativa (R$ 4 padrão) e ajuste depois. O app é um **simulador** — teste cenários.

---

## Sobre a agenda

### O que é overbooking?

Agendar um pouco **além** da capacidade, porque alguns pacientes faltam. Ex.: capacidade 60 min + overbooking 20 min = até 80 min agendados.

### Overbooking não gera caos?

Pode gerar atraso se exagerado. Por isso existe **Lambda** — penaliza atraso na otimização. A clínica define política.

### Por que alguns pacientes não são alocados?

Capacidade insuficiente, incompatibilidade de modalidade ou solver não encontrou slot viável. Aumente capacidade/overbooking ou reduza agendamentos do dia.

### O que é Lambda na prática?

**Termômetro conservador ↔ agressivo.** Alto = menos lotação, menos atraso. Baixo = mais pacientes, mais receita, mais risco de fila.

---

## Sobre a interface

### Os sliders retreinam o modelo?

**Não.** Só mudam a simulação do dia (quantos pacientes, orçamento, capacidade). O modelo permanece o mesmo.

### Por que "Agendamentos do dia" não é um calendário real?

No MVP, pega os **primeiros N registros** do CSV como proxy de "um dia". Em produção, filtraria por data real.

### Posso exportar a lista de quem ligar?

Streamlit permite copiar tabelas. Integração futura exportaria CSV ou enviaria ao sistema de agendamento.

---

## Sobre privacidade e ética

### O app usa nome ou CPF?

**Não.** Apenas IDs anonimizados e variáveis operacionais.

### Paciente com score alto é punido?

**Não.** Recebe **mais atenção** (ligação, reforço) — para **aumentar** chance de comparecimento, não para excluir.

### Está em conformidade com LGPD?

O MVP usa dados sintéticos. Em produção: pseudonimização, acesso restrito, base legal, política de retenção. Ver [07_ETICA_E_PRIVACIDADE.md](07_ETICA_E_PRIVACIDADE.md).

---

## Sobre implantação real

### O que falta para usar na clínica?

1. Dados históricos reais anonimizados  
2. Calibrar custos e eficácia das intervenções  
3. Integração com sistema de agendamento  
4. Retreino periódico e monitoramento  

### Com que frequência atualizar o modelo?

Sugestão: **trimestral** ou após mudanças operacionais relevantes.

### Como medir se funcionou?

Compare taxa de comparecimento, receita por slot e tempo de ociosidade **antes e depois** — idealmente com teste A/B.

---

## Problemas técnicos

### `streamlit` não é reconhecido

Use: `python -m streamlit run app.py`

### App trava na primeira vez

Aguarde — treinamento em andamento. Verifique se `data/agendamentos.csv` existe.

### Erro de dependências

Execute: `pip install -r requirements.txt`

---

## Ainda com dúvidas?

Consulte o [Guia completo](GUIA_COMPLETO.md) ou o [Glossário](05_GLOSSARIO.md).
