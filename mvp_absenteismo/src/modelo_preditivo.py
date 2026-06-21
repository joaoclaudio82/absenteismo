"""
Camada preditiva (secao 8 da proposta).
Estima p_i = P(falta | caracteristicas) para cada agendamento.

Treina dois modelos:
  - Regressao Logistica: baseline interpretavel, expoe coeficientes.
  - Gradient Boosting calibrado: captura relacoes nao lineares.

A calibracao de probabilidades e essencial: o otimizador da secao 10
consome p_i diretamente, entao probabilidades mal calibradas degradam
a alocacao da agenda.

Uso:
    python -m src.modelo_preditivo --dados data/agendamentos.csv
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss, classification_report, confusion_matrix, roc_auc_score)
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERICAS = [
    "idade", "faltas_previas", "comparecimentos_previos", "distancia_km",
    "duracao_min", "receita_estimada", "antecedencia_dias", "tentativas_contato",
]
BINARIAS = ["paciente_novo", "necessita_preparo", "usa_contraste", "confirmado"]
CATEGORICAS = ["modalidade", "canal_agendamento", "convenio", "turno", "dia_semana"]
ALVO = "faltou"


def _preprocessador() -> ColumnTransformer:
    return ColumnTransformer([
        ("num", StandardScaler(), NUMERICAS),
        ("bin", "passthrough", BINARIAS),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
    ])


def treinar(df: pd.DataFrame, seed: int = 42) -> dict:
    X = df[NUMERICAS + BINARIAS + CATEGORICAS]
    y = df[ALVO]

    if "id_paciente" in df.columns:
        # Um mesmo paciente nao pode aparecer no treino e no teste, pois isso
        # produziria uma avaliacao otimista em bases com consultas repetidas.
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=seed)
        idx_tr, idx_te = next(splitter.split(X, y, groups=df["id_paciente"]))
        X_tr, X_te = X.iloc[idx_tr], X.iloc[idx_te]
        y_tr, y_te = y.iloc[idx_tr], y.iloc[idx_te]
        pacientes_tr = set(df.iloc[idx_tr]["id_paciente"])
        pacientes_te = set(df.iloc[idx_te]["id_paciente"])
        split_info = {
            "estrategia": "por_paciente",
            "n_pacientes_treino": len(pacientes_tr),
            "n_pacientes_teste": len(pacientes_te),
            "pacientes_em_comum": len(pacientes_tr & pacientes_te),
        }
    else:
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.25, random_state=seed, stratify=y)
        split_info = {
            "estrategia": "estratificado_por_agendamento",
            "n_pacientes_treino": None,
            "n_pacientes_teste": None,
            "pacientes_em_comum": None,
        }

    pre = _preprocessador()

    # baseline interpretavel
    logit = Pipeline([
        ("pre", pre),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ]).fit(X_tr, y_tr)

    # modelo nao linear calibrado
    gb_base = Pipeline([
        ("pre", _preprocessador()),
        ("clf", GradientBoostingClassifier(random_state=seed)),
    ])
    gb = CalibratedClassifierCV(gb_base, method="isotonic", cv=3).fit(X_tr, y_tr)

    resultados = {}
    for nome, modelo in [("regressao_logistica", logit), ("gradient_boosting", gb)]:
        p = modelo.predict_proba(X_te)[:, 1]
        pred = (p >= 0.5).astype(int)
        resultados[nome] = {
            "auc_roc": round(roc_auc_score(y_te, p), 4),
            "brier": round(brier_score_loss(y_te, p), 4),
            "matriz_confusao": confusion_matrix(y_te, pred).tolist(),
            "relatorio": classification_report(y_te, pred, output_dict=True, zero_division=0),
        }

    return {"logit": logit, "gb": gb, "metricas": resultados,
            "split_info": split_info,
            "X_te": X_te, "y_te": y_te}


def coeficientes_logit(logit: Pipeline) -> pd.DataFrame:
    pre = logit.named_steps["pre"]
    nomes = (NUMERICAS + BINARIAS +
             list(pre.named_transformers_["cat"].get_feature_names_out(CATEGORICAS)))
    coefs = logit.named_steps["clf"].coef_[0]
    return (pd.DataFrame({"variavel": nomes, "coeficiente": coefs})
            .assign(odds_ratio=lambda d: np.exp(d["coeficiente"]))
            .sort_values("coeficiente", key=abs, ascending=False)
            .reset_index(drop=True))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="data/agendamentos.csv")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.dados)
    r = treinar(df, args.seed)

    print("=== Metricas de avaliacao (secao 8.3) ===")
    print(json.dumps({k: {"auc_roc": v["auc_roc"], "brier": v["brier"]}
                      for k, v in r["metricas"].items()}, indent=2))

    print("\n=== Top fatores de risco (regressao logistica) ===")
    print(coeficientes_logit(r["logit"]).head(10).to_string(index=False))


if __name__ == "__main__":
    main()
