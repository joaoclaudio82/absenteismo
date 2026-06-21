"""
Testes de regressao do MVP de absenteismo.
Rodar com: pytest -q   (a partir da raiz do projeto)
"""
import numpy as np
import pandas as pd
import pytest

from src.decisao import classificar_risco, otimizar_confirmacoes
from src.gerar_dados import gerar
from src.modelo_preditivo import treinar
from src.otimizacao_agenda import otimizar_agenda


@pytest.fixture(scope="module")
def df():
    return gerar(3000, seed=1)


def test_gerador_colunas_e_alvo(df):
    assert "faltou" in df.columns
    assert set(df["faltou"].unique()) <= {0, 1}
    assert 0.15 < df["faltou"].mean() < 0.60  # taxa plausivel


def test_gerador_preserva_desfechos_completos(df):
    desfechos_validos = {
        "compareceu",
        "faltou_sem_aviso",
        "cancelou_em_cima_hora",
        "cancelou_antecedencia",
        "remarcou",
    }
    assert set(df["desfecho"].unique()) <= desfechos_validos
    assert not df["desfecho"].str.endswith(("_sem", "_e", "_a")).any()


def test_faixas_de_risco_cobrem_tudo():
    p = np.array([0.05, 0.20, 0.45, 0.75])
    r = classificar_risco(p)
    assert list(r["nivel_risco"]) == ["baixo", "medio", "alto", "muito_alto"]
    assert r["nivel_risco"].notna().all()


def test_modelo_aprende_acima_do_acaso(df):
    r = treinar(df, seed=1)
    assert r["metricas"]["gradient_boosting"]["auc_roc"] > 0.65
    assert r["metricas"]["regressao_logistica"]["auc_roc"] > 0.65


def test_confirmacao_respeita_orcamento():
    rng = np.random.default_rng(0)
    receita = rng.uniform(100, 900, 60)
    p = rng.uniform(0.05, 0.7, 60)
    res = otimizar_confirmacoes(receita, p, orcamento=40.0, custo_intervencao=4.0)
    assert res["status"] == "Optimal"
    assert res["custo_total"] <= 40.0 + 1e-6
    assert res["ganho_esperado"] >= 0


def test_agenda_respeita_alocacao_unica_e_overbooking():
    rng = np.random.default_rng(2)
    n = 40
    pac = pd.DataFrame({
        "id_agendamento": range(1, n + 1),
        "duracao_min": rng.choice([15, 20, 30], n),
        "prob_falta": rng.uniform(0.05, 0.6, n),
        "receita_estimada": rng.uniform(100, 900, n),
        "modalidade": rng.choice(["tomografia", "radiografia"], n),
    })
    horarios = ["08:00", "09:00", "10:00"]
    modalidades = ["tomografia", "radiografia"]
    cap = {(t, m): 60 for t in horarios for m in modalidades}
    ob = {(t, m): 15 for t in horarios for m in modalidades}
    res = otimizar_agenda(pac, horarios, cap, ob, lam=2.0)

    assert res.status == "Optimal"
    # alocacao unica: cada paciente aparece no maximo uma vez
    assert res.alocacoes["id_agendamento"].is_unique
    # overbooking: ocupacao bruta nunca passa de C + O
    for _, row in res.ocupacao.iterrows():
        assert row["ocup_bruta_min"] <= row["capacidade_min"] + row["overbooking_min"] + 1e-6


def test_paciente_so_vai_para_sua_modalidade():
    pac = pd.DataFrame({
        "id_agendamento": [1, 2],
        "duracao_min": [30, 15],
        "prob_falta": [0.1, 0.1],
        "receita_estimada": [600, 90],
        "modalidade": ["tomografia", "radiografia"],
    })
    horarios = ["08:00"]
    modalidades = ["tomografia", "radiografia"]
    cap = {(t, m): 60 for t in horarios for m in modalidades}
    ob = {(t, m): 0 for t in horarios for m in modalidades}
    res = otimizar_agenda(pac, horarios, cap, ob)
    for _, row in res.alocacoes.iterrows():
        esperado = "tomografia" if row["id_agendamento"] == 1 else "radiografia"
        assert row["modalidade"] == esperado
