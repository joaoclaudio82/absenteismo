"""
Camada decisoria (secoes 9 e 11 da proposta).

1) Classifica cada agendamento em faixa de risco (Tabela 1) e associa
   a acao operacional recomendada.

2) Otimiza as acoes de confirmacao ativa sob orcamento limitado.
   Maximiza o ganho esperado sum_i [ r_i (p_i - p'_i) - c_i ] z_i
   sujeito a sum_i c_i z_i <= B.
   Formulado como problema da mochila 0/1 e resolvido com PuLP.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pulp

from .solver import resolver

# Tabela 1 da proposta: limites e acoes por faixa de risco
FAIXAS = [
    (0.00, 0.15, "baixo",     "Lembrete automatico simples (WhatsApp/SMS)."),
    (0.15, 0.35, "medio",     "Mensagem reforcada com solicitacao de confirmacao."),
    (0.35, 0.60, "alto",      "Ligacao ativa, reforco de preparo e confirmacao obrigatoria."),
    (0.60, 1.01, "muito_alto","Confirmacao obrigatoria; libera vaga se sem resposta + lista de espera."),
]


def classificar_risco(p: np.ndarray | pd.Series) -> pd.DataFrame:
    p = np.asarray(p, dtype=float)
    nivel = np.empty(len(p), dtype=object)
    acao = np.empty(len(p), dtype=object)
    for lo, hi, nome, descricao in FAIXAS:
        mask = (p >= lo) & (p < hi)
        nivel[mask] = nome
        acao[mask] = descricao
    return pd.DataFrame({"prob_falta": p.round(4), "nivel_risco": nivel,
                         "acao_recomendada": acao})


def otimizar_confirmacoes(
    receita: np.ndarray,
    p_falta: np.ndarray,
    reducao_relativa: float = 0.40,
    custo_intervencao: float = 4.0,
    orcamento: float = 200.0,
) -> dict:
    """
    Decide quais agendamentos recebem intervencao ativa (secao 11).

    reducao_relativa: fracao de reducao de p_i apos intervencao.
                      p'_i = p_i * (1 - reducao_relativa)
    custo_intervencao: c_i (ex.: custo de uma ligacao).
    orcamento: B, limite total de custo (ou nro de intervencoes * custo).
    """
    receita = np.asarray(receita, dtype=float)
    p_falta = np.asarray(p_falta, dtype=float)
    n = len(receita)

    p_pos = p_falta * (1.0 - reducao_relativa)
    ganho = receita * (p_falta - p_pos) - custo_intervencao  # coef. de z_i

    prob = pulp.LpProblem("priorizacao_confirmacao", pulp.LpMaximize)
    z = [pulp.LpVariable(f"z_{i}", cat="Binary") for i in range(n)]

    prob += pulp.lpSum(ganho[i] * z[i] for i in range(n))
    prob += pulp.lpSum(custo_intervencao * z[i] for i in range(n)) <= orcamento
    # so vale intervir quando o ganho liquido e positivo
    for i in range(n):
        if ganho[i] <= 0:
            prob += z[i] == 0

    resolver(prob)

    selecionados = np.array([int(z[i].value() or 0) for i in range(n)], dtype=int)
    ganho_total = float(sum(ganho[i] * selecionados[i] for i in range(n)))
    return {
        "selecionados": selecionados,
        "n_intervencoes": int(selecionados.sum()),
        "ganho_esperado": round(ganho_total, 2),
        "custo_total": round(float(custo_intervencao * selecionados.sum()), 2),
        "status": pulp.LpStatus[prob.status],
    }
