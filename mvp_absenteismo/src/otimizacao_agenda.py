"""
Camada de otimizacao da agenda (secao 10 da proposta).

Programacao linear inteira que aloca pacientes em horarios x modalidades
maximizando receita esperada, descontando penalizacao por atraso esperado:

    max  sum_{i,t,m} r_i (1 - p_i) x_{itm}  -  lambda * sum_{t,m} A_{tm}

sujeito a:
    (10.5) alocacao unica:      sum_{t,m} x_{itm} <= 1            para todo i
    (10.6) capacidade nominal:  C_tm e o limite sem atraso esperado
    (10.7) overbooking:         sum_i d_i x_{itm} <= C_tm + O_tm   para todo t,m
    (10.8) atraso esperado:     A_tm >= sum_i d_i(1-p_i) x_{itm} - C_tm

A capacidade nominal nao e uma restricao rigida sobre a ocupacao esperada:
quando ela e ultrapassada, o excesso e representado por A_tm e penalizado na
funcao objetivo. O limite rigido continua sendo capacidade + overbooking.
Assim, lambda controla de fato o equilibrio entre receita e risco de atraso.

Apenas pacientes compativeis com a modalidade m podem ser alocados.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import pulp


@dataclass
class ResultadoAgenda:
    alocacoes: pd.DataFrame      # i, t, m alocados
    receita_esperada: float
    atraso_total: float
    ocupacao: pd.DataFrame       # por (t, m): esperada, bruta, capacidade
    status: str


def otimizar_agenda(
    pacientes: pd.DataFrame,
    horarios: list,
    capacidade: dict,            # {(t, m): C_tm}
    overbooking: dict,           # {(t, m): O_tm}
    lam: float = 2.0,
    col_id: str = "id_agendamento",
    col_dur: str = "duracao_min",
    col_prob: str = "prob_falta",
    col_receita: str = "receita_estimada",
    col_modalidade: str = "modalidade",
) -> ResultadoAgenda:
    I = pacientes[col_id].tolist()
    d = dict(zip(I, pacientes[col_dur]))
    p = dict(zip(I, pacientes[col_prob]))
    r = dict(zip(I, pacientes[col_receita]))
    mod_pac = dict(zip(I, pacientes[col_modalidade]))

    M = sorted(pacientes[col_modalidade].unique().tolist())
    T = list(horarios)
    pares_tm = [(t, m) for t in T for m in M]

    prob = pulp.LpProblem("otimizacao_agenda", pulp.LpMaximize)

    # x_itm so existe quando paciente i e da modalidade m (compatibilidade)
    x = {(i, t, m): pulp.LpVariable(f"x_{i}_{t}_{m}", cat="Binary")
         for i in I for t in T for m in M if mod_pac[i] == m}
    A = {(t, m): pulp.LpVariable(f"A_{t}_{m}", lowBound=0) for (t, m) in pares_tm}

    # Funcao objetivo (10.4 + 10.8)
    receita = pulp.lpSum(r[i] * (1 - p[i]) * x[(i, t, m)] for (i, t, m) in x)
    penal = lam * pulp.lpSum(A[(t, m)] for (t, m) in pares_tm)
    prob += receita - penal

    # (10.5) alocacao unica
    for i in I:
        termos = [x[(i, t, m)] for t in T for m in M if (i, t, m) in x]
        if termos:
            prob += pulp.lpSum(termos) <= 1

    for (t, m) in pares_tm:
        C = capacidade.get((t, m), 0)
        O = overbooking.get((t, m), 0)
        ocup_esp = pulp.lpSum(d[i] * (1 - p[i]) * x[(i, t, m)]
                              for i in I if (i, t, m) in x)
        ocup_bruta = pulp.lpSum(d[i] * x[(i, t, m)]
                                for i in I if (i, t, m) in x)
        # A capacidade nominal marca o ponto a partir do qual existe atraso
        # esperado. Nao deve ser tambem uma restricao rigida, pois isso
        # obrigaria A a zero e tornaria o parametro lambda inoperante.
        prob += ocup_bruta <= C + O                # (10.7)
        prob += A[(t, m)] >= ocup_esp - C          # (10.8)

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    linhas = [{"id_agendamento": i, "horario": t, "modalidade": m}
              for (i, t, m) in x if (x[(i, t, m)].value() or 0) > 0.5]
    aloc = pd.DataFrame(linhas)

    ocup_rows = []
    for (t, m) in pares_tm:
        ids = aloc.loc[(aloc.get("horario") == t) & (aloc.get("modalidade") == m),
                       "id_agendamento"].tolist() if not aloc.empty else []
        esp = sum(d[i] * (1 - p[i]) for i in ids)
        bruta = sum(d[i] for i in ids)
        ocup_rows.append({"horario": t, "modalidade": m,
                          "ocup_esperada_min": round(esp, 1),
                          "ocup_bruta_min": round(bruta, 1),
                          "capacidade_min": capacidade.get((t, m), 0),
                          "overbooking_min": overbooking.get((t, m), 0)})

    return ResultadoAgenda(
        alocacoes=aloc,
        receita_esperada=round(float(pulp.value(receita) or 0), 2),
        atraso_total=round(float(sum((A[(t, m)].value() or 0) for (t, m) in pares_tm)), 1),
        ocupacao=pd.DataFrame(ocup_rows),
        status=pulp.LpStatus[prob.status],
    )
