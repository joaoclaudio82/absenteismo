"""
Gera base sintetica de agendamentos para clinica de diagnostico por imagem.
Reproduz padroes realistas de absenteismo descritos na proposta CPDI:
o risco de falta depende de historico do paciente, antecedencia, turno,
modalidade, canal de marcacao e status de confirmacao.

Uso:
    python -m src.gerar_dados --n 8000 --saida data/agendamentos.csv
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd

MODALIDADES = {
    "ultrassonografia": {"duracao": 20, "receita": 180, "preparo": 0.3, "contraste": 0.0},
    "tomografia":       {"duracao": 30, "receita": 650, "preparo": 0.5, "contraste": 0.4},
    "ressonancia":      {"duracao": 45, "receita": 950, "preparo": 0.4, "contraste": 0.3},
    "radiografia":      {"duracao": 15, "receita": 90,  "preparo": 0.1, "contraste": 0.0},
    "mamografia":       {"duracao": 25, "receita": 220, "preparo": 0.2, "contraste": 0.0},
    "densitometria":    {"duracao": 20, "receita": 200, "preparo": 0.1, "contraste": 0.0},
}
CANAIS = ["telefone", "whatsapp", "site", "presencial", "encaminhamento"]
TURNOS = ["manha", "tarde", "noite"]
CONVENIOS = ["particular", "convenio_a", "convenio_b", "convenio_c", "sus"]


def gerar(n: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    modalidade = rng.choice(list(MODALIDADES), size=n,
                            p=[0.30, 0.18, 0.12, 0.18, 0.12, 0.10])
    canal = rng.choice(CANAIS, size=n, p=[0.20, 0.35, 0.20, 0.15, 0.10])
    turno = rng.choice(TURNOS, size=n, p=[0.45, 0.40, 0.15])
    dia_semana = rng.integers(0, 6, size=n)  # 0=seg ... 5=sab
    convenio = rng.choice(CONVENIOS, size=n, p=[0.25, 0.25, 0.20, 0.15, 0.15])

    idade = np.clip(rng.normal(45, 16, size=n), 5, 95).astype(int)
    antecedencia = rng.integers(0, 45, size=n)  # dias entre marcacao e exame
    paciente_novo = rng.random(n) < 0.35
    faltas_previas = rng.poisson(0.6, size=n)
    comparec_previos = rng.poisson(2.5, size=n)
    tentativas_contato = rng.integers(0, 4, size=n)
    confirmado = rng.random(n) < 0.55
    distancia_km = np.clip(rng.exponential(8, size=n), 0.5, 60)

    dur = np.array([MODALIDADES[m]["duracao"] for m in modalidade])
    rec = np.array([MODALIDADES[m]["receita"] for m in modalidade])
    prep_p = np.array([MODALIDADES[m]["preparo"] for m in modalidade])
    contraste_p = np.array([MODALIDADES[m]["contraste"] for m in modalidade])
    necessita_preparo = rng.random(n) < prep_p
    usa_contraste = rng.random(n) < contraste_p

    # log-odds de falta -> probabilidade verdadeira (oculta do modelo)
    z = (-1.7
         + 0.030 * antecedencia
         + 0.45 * faltas_previas
         - 0.18 * comparec_previos
         + 0.9 * (~confirmado)
         + 0.6 * paciente_novo
         + 0.4 * (turno == "noite")
         + 0.25 * (canal == "telefone")
         - 0.35 * (canal == "presencial")
         + 0.012 * distancia_km
         + 0.3 * necessita_preparo
         + 0.5 * (convenio == "sus")
         - 0.008 * idade)
    p_real = 1.0 / (1.0 + np.exp(-z))
    faltou = (rng.random(n) < p_real).astype(int)

    # desfecho detalhado
    # dtype=object evita que o NumPy fixe o tamanho do texto com base em
    # "compareceu" e trunque desfechos mais longos nas atribuicoes seguintes.
    desfecho = np.full(n, "compareceu", dtype=object)
    faltantes = np.where(faltou == 1)[0]
    desfecho[faltantes] = rng.choice(
        ["faltou_sem_aviso", "cancelou_em_cima_hora", "cancelou_antecedencia", "remarcou"],
        size=len(faltantes), p=[0.50, 0.20, 0.18, 0.12])

    return pd.DataFrame({
        "id_agendamento": np.arange(1, n + 1),
        "id_paciente": rng.integers(1, n // 2 + 1, size=n),
        "idade": idade,
        "paciente_novo": paciente_novo.astype(int),
        "faltas_previas": faltas_previas,
        "comparecimentos_previos": comparec_previos,
        "distancia_km": distancia_km.round(1),
        "modalidade": modalidade,
        "duracao_min": dur,
        "receita_estimada": rec,
        "necessita_preparo": necessita_preparo.astype(int),
        "usa_contraste": usa_contraste.astype(int),
        "canal_agendamento": canal,
        "convenio": convenio,
        "turno": turno,
        "dia_semana": dia_semana,
        "antecedencia_dias": antecedencia,
        "tentativas_contato": tentativas_contato,
        "confirmado": confirmado.astype(int),
        "desfecho": desfecho,
        "faltou": faltou,
    })


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--saida", default="data/agendamentos.csv")
    args = ap.parse_args()

    df = gerar(args.n, args.seed)
    df.to_csv(args.saida, index=False)
    taxa = df["faltou"].mean()
    print(f"Gerados {len(df)} agendamentos em {args.saida}")
    print(f"Taxa de absenteismo simulada: {taxa:.1%}")


if __name__ == "__main__":
    main()
