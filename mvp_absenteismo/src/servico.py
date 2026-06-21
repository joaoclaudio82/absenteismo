"""
Camada de servico para a interface grafica.

Separa o treino (caro, feito uma vez e persistido) do escoramento e da
otimizacao (rapidos, interativos). Evita retreinar o modelo a cada clique.
"""
from __future__ import annotations

import os

import joblib
import pandas as pd

from .modelo_preditivo import coeficientes_logit, treinar

MODELO_PATH = "data/modelo.joblib"


def treinar_e_salvar(dados_csv: str, seed: int = 42, caminho: str = MODELO_PATH) -> dict:
    df = pd.read_csv(dados_csv)
    r = treinar(df, seed)
    pacote = {
        "gb": r["gb"],
        "logit": r["logit"],
        "metricas": r["metricas"],
        "split_info": r["split_info"],
        "coeficientes": coeficientes_logit(r["logit"]),
    }
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    joblib.dump(pacote, caminho)
    return pacote


def carregar_modelo(caminho: str = MODELO_PATH):
    if not os.path.exists(caminho):
        return None
    return joblib.load(caminho)


def escorar(df: pd.DataFrame, modelo) -> pd.DataFrame:
    """Adiciona coluna prob_falta usando o modelo calibrado (gb)."""
    from .modelo_preditivo import BINARIAS, CATEGORICAS, NUMERICAS
    X = df[NUMERICAS + BINARIAS + CATEGORICAS]
    out = df.copy()
    out["prob_falta"] = modelo["gb"].predict_proba(X)[:, 1]
    return out
