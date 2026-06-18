# Ética, privacidade e uso responsável

Como o app lida com dados de pacientes e quais cuidados adotar em produção.

---

## Princípio fundamental

> O score de risco é **ferramenta de apoio à decisão**, nunca mecanismo de **exclusão** de pacientes.

O objetivo é **aumentar comparecimento** e **melhorar operação** — não penalizar quem tem histórico de faltas.

---

## O que o app faz (uso ético)

| Faz | Por quê |
|---|---|
| Estima probabilidade de falta | Direcionar esforço de confirmação |
| Sugere tipo de contato por faixa | Protocolo proporcional ao risco |
| Prioriza ligações sob orçamento | Maximizar retorno do esforço |
| Otimiza agenda com risco esperado | Melhor uso de equipamentos |

---

## O que o app NÃO deve fazer

| Não faz / não deve | Por quê |
|---|---|
| Cancelar agendamento automaticamente | Decisão clínica e administrativa humana |
| Negar atendimento por score alto | Discriminação operacional inaceitável |
| Expor identidade do paciente na interface pública | Privacidade |
| Usar score como critério clínico | Fora do escopo; não é diagnóstico médico |
| Compartilhar scores com terceiros | Violação de confidencialidade |

---

## Dados e privacidade (LGPD)

### No MVP

- Base **sintética** — nenhum paciente real.
- IDs numéricos fictícios (`id_paciente`, `id_agendamento`).

### Em produção

Requisitos mínimos:

1. **Pseudonimização** — substituir nome/CPF por identificador interno irreversível na camada analítica.
2. **Minimização** — usar apenas variáveis necessárias ao modelo (já definidas no código).
3. **Acesso restrito** — perfis autorizados (gestão, TI, equipe de confirmação conforme política).
4. **Base legal** — legítimo interesse ou execução de contrato, documentado.
5. **Retenção** — prazo definido; descarte após período necessário.
6. **Direitos do titular** — procedimento para acesso, correção e eliminação quando aplicável.
7. **Segurança** — criptografia em trânsito/repouso, logs de acesso, ambiente controlado.

### Variáveis que o modelo usa (sem dados sensíveis de saúde)

Operacionais: idade, distância, histórico de faltas, modalidade, convênio, canal, turno, confirmação.

**Não usa:** diagnóstico, laudo, condição clínica, raça, religião ou dados genéticos.

---

## Viés e equidade

### Riscos a monitorar

- **Viés histórico:** se certos grupos faltaram mais por barreiras de acesso (transporte, horário), o modelo pode perpetuar padrão — não a intenção, mas efeito possível.
- **Convênio SUS:** pode aparecer como fator de risco por correlatos operacionais (antecedência, canal), não por discriminação intencional.

### Mitigações

- Revisar periodicamente coeficientes e impacto por subgrupo.
- Tratar score como **probabilidade operacional**, não julgamento moral.
- Garantir que intervenções **ajudam** o paciente a comparecer (lembrete, transporte, reagendamento flexível).

---

## Transparência com pacientes

Recomendações para a clínica:

- Informar na política de privacidade que dados de agendamento podem ser usados para **melhorar confirmações e agenda**.
- Não é obrigatório informar score individual, mas deve haver canal para dúvidas sobre tratamento de dados.
- Contatos (ligações, SMS) devem seguir preferência e horário do paciente.

---

## Overbooking e responsabilidade clínica

Overbooking é **política de gestão**, não decisão automática do app.

- O app **quantifica** trade-off receita vs. atraso.
- A clínica **define** limites aceitáveis (Lambda, overbooking máximo).
- Supervisão médica valida impacto na qualidade do atendimento.

---

## Governança sugerida

| Papel | Responsabilidade |
|---|---|
| Gestão | Aprovar parâmetros (orçamento, overbooking, lambda) |
| DPO / Jurídico | Conformidade LGPD, bases legais |
| TI / Dados | Segurança, anonimização, integração |
| Operação | Executar confirmações; feedback sobre eficácia |
| Estatística / TI | Retreino, monitoramento de métricas e viés |

---

## Checklist antes de ir para produção

- [ ] Dados anonimizados e contrato/base legal documentados  
- [ ] Política de retenção e descarte definida  
- [ ] Acesso por perfil implementado  
- [ ] Equipe treinada: score ≠ exclusão  
- [ ] Parâmetros calibrados com operação real  
- [ ] Plano de monitoramento trimestral  
- [ ] Canal de dúvidas do titular sobre dados  

---

## Referência na proposta original

A proposta CPDI dedica a seção 16 à privacidade e uso responsável. Este app segue essa orientação: pseudonimização, acesso restrito e score como apoio — nunca exclusão.

---

## Próxima leitura

- [Ideia e objetivo](01_IDEA_E_OBJETIVO.md)
- [Perguntas frequentes](06_PERGUNTAS_FREQUENTES.md)
- [Guia completo](GUIA_COMPLETO.md)
