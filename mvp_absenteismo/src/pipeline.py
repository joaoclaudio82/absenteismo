"""
Pipeline de ponta a ponta (visao geral, secao 6):
    Dados -> Modelo Preditivo -> Probabilidade -> Otimizacao -> Agenda + Acoes

Executa as tres camadas e imprime os indicadores de desempenho (secao 13).

Uso:
    python -m src.pipeline --dados data/agendamentos.csv
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from .decisao import classificar_risco, otimizar_confirmacoes
from .modelo_preditivo import treinar
from .otimizacao_agenda import otimizar_agenda

HORARIOS = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]


def montar_capacidades(modalidades: list, horarios: list,
                       cap_min: int = 60, ob_min: int = 20) -> tuple[dict, dict]:
    capacidade = {(t, m): cap_min for t in horarios for m in modalidades}
    overbooking = {(t, m): ob_min for t in horarios for m in modalidades}
    return capacidade, overbooking


def executar(dados: str, n_agenda: int = 120, lam: float = 2.0,
             orcamento_confirmacao: float = 200.0, seed: int = 42) -> dict:
    df = pd.read_csv(dados)

    # --- Camada preditiva ---
    r = treinar(df, seed)
    modelo = r["gb"]  # calibrado, usado pelo otimizador

    # escora o conjunto de teste como "demanda do dia"
    X_te, y_te = r["X_te"], r["y_te"]
    base = df.loc[X_te.index].copy()
    base["prob_falta"] = modelo.predict_proba(X_te)[:, 1]

    # --- Camada decisoria: faixas de risco ---
    risco = classificar_risco(base["prob_falta"])
    base = base.reset_index(drop=True)
    base[["nivel_risco", "acao_recomendada"]] = risco[["nivel_risco", "acao_recomendada"]]

    # recorte do dia para agendar
    dia = base.head(n_agenda).reset_index(drop=True)

    # --- Camada decisoria: priorizacao de confirmacoes (secao 11) ---
    conf = otimizar_confirmacoes(
        receita=dia["receita_estimada"].values,
        p_falta=dia["prob_falta"].values,
        orcamento=orcamento_confirmacao,
    )
    dia["confirmacao_ativa"] = conf["selecionados"]

    # --- Camada de otimizacao da agenda (secao 10) ---
    modalidades = sorted(dia["modalidade"].unique().tolist())
    capacidade, overbooking = montar_capacidades(modalidades, HORARIOS)
    agenda = otimizar_agenda(dia, HORARIOS, capacidade, overbooking, lam=lam)

    return {"metricas_modelo": r["metricas"], "base_dia": dia,
            "confirmacao": conf, "agenda": agenda}


def imprimir_indicadores(res: dict) -> None:
    dia = res["base_dia"]
    agenda = res["agenda"]
    conf = res["confirmacao"]

    print("\n" + "=" * 60)
    print("INDICADORES DE DESEMPENHO (secao 13)")
    print("=" * 60)

    print("\n-- Distribuicao por nivel de risco --")
    print(dia["nivel_risco"].value_counts().reindex(
        ["baixo", "medio", "alto", "muito_alto"]).fillna(0).astype(int).to_string())

    print("\n-- Priorizacao de confirmacao ativa (secao 11) --")
    print(f"Intervencoes selecionadas : {conf['n_intervencoes']} de {len(dia)}")
    print(f"Ganho esperado liquido    : R$ {conf['ganho_esperado']}")
    print(f"Custo total das acoes     : R$ {conf['custo_total']}")

    print("\n-- Otimizacao da agenda (secao 10) --")
    print(f"Status do solver          : {agenda.status}")
    print(f"Pacientes alocados        : {len(agenda.alocacoes)} de {len(dia)}")
    print(f"Receita esperada          : R$ {agenda.receita_esperada}")
    print(f"Atraso esperado total     : {agenda.atraso_total} min")

    receita_potencial = float(dia["receita_estimada"].sum())
    receita_perda_faltas = float((dia["receita_estimada"] * dia["prob_falta"]).sum())
    print(f"Receita potencial (bruta) : R$ {round(receita_potencial, 2)}")
    print(f"Perda esperada por faltas : R$ {round(receita_perda_faltas, 2)}")

    print("\n-- Ocupacao por horario/modalidade (amostra) --")
    print(agenda.ocupacao.head(10).to_string(index=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="data/agendamentos.csv")
    ap.add_argument("--n-agenda", type=int, default=120)
    ap.add_argument("--lam", type=float, default=2.0)
    ap.add_argument("--orcamento", type=float, default=200.0)
    args = ap.parse_args()

    res = executar(args.dados, args.n_agenda, args.lam, args.orcamento)
    imprimir_indicadores(res)


if __name__ == "__main__":
    main()
