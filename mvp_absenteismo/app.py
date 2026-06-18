"""
Interface grafica do MVP de reducao de absenteismo (CPDI).

Executar a partir da raiz do projeto:
    streamlit run app.py

Abas:
  1. Visao geral      - indicadores e desempenho do modelo
  2. Risco            - escoragem e classificacao por faixa de risco
  3. Confirmacoes     - priorizacao de acoes ativas sob orcamento
  4. Agenda           - otimizacao da alocacao (PLI)
"""
from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.decisao import FAIXAS, classificar_risco, otimizar_confirmacoes
from src.gerar_dados import gerar
from src.otimizacao_agenda import otimizar_agenda
from src.servico import carregar_modelo, escorar, treinar_e_salvar

DADOS_CSV = "data/agendamentos.csv"
HORARIOS = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
CORES_RISCO = {"baixo": "#2e7d32", "medio": "#f9a825",
               "alto": "#ef6c00", "muito_alto": "#c62828"}

st.set_page_config(page_title="Absenteismo CPDI", layout="wide", page_icon="🩺")


# ---------- carregamento com cache ----------
@st.cache_data(show_spinner=False)
def carregar_base() -> pd.DataFrame:
    if not os.path.exists(DADOS_CSV):
        os.makedirs("data", exist_ok=True)
        gerar(8000, seed=42).to_csv(DADOS_CSV, index=False)
    return pd.read_csv(DADOS_CSV)


@st.cache_resource(show_spinner="Treinando modelo (primeira execucao)...")
def obter_modelo():
    m = carregar_modelo()
    if m is None:
        m = treinar_e_salvar(DADOS_CSV)
    return m


@st.cache_data(show_spinner=False)
def escorar_base(_modelo, n_rows: int) -> pd.DataFrame:
    df = carregar_base().head(n_rows)
    scored = escorar(df, _modelo)
    risco = classificar_risco(scored["prob_falta"])
    scored = scored.reset_index(drop=True)
    scored[["nivel_risco", "acao_recomendada"]] = risco[["nivel_risco", "acao_recomendada"]]
    return scored


# ---------- cabecalho ----------
st.title("🩺 Estrategia Inteligente para Reducao do Absenteismo")
st.caption("Clinica de diagnostico por imagem | predicao + otimizacao de agenda")

df_base = carregar_base()
modelo = obter_modelo()

with st.sidebar:
    st.header("Parametros")
    n_dia = st.slider("Agendamentos do dia", 40, 400, 120, step=20)
    st.divider()
    st.subheader("Confirmacao ativa (sec. 11)")
    orcamento = st.slider("Orcamento diario (R$)", 50, 600, 200, step=10)
    custo_int = st.slider("Custo por intervencao (R$)", 1.0, 15.0, 4.0, step=0.5)
    reducao = st.slider("Reducao de risco da acao", 0.1, 0.7, 0.4, step=0.05)
    st.divider()
    st.subheader("Agenda (sec. 10)")
    cap_min = st.slider("Capacidade/bloco (min)", 30, 120, 60, step=10)
    ob_min = st.slider("Overbooking/bloco (min)", 0, 60, 20, step=5)
    lam = st.slider("Lambda (penaliza atraso)", 0.0, 15.0, 2.0, step=0.5)

dia = escorar_base(modelo, n_dia)

aba1, aba2, aba3, aba4 = st.tabs(
    ["📊 Visao geral", "🎯 Risco", "📞 Confirmacoes", "🗓️ Agenda"])


# ===================== ABA 1: VISAO GERAL =====================
with aba1:
    taxa_real = df_base["faltou"].mean()
    perda = float((dia["receita_estimada"] * dia["prob_falta"]).sum())
    potencial = float(dia["receita_estimada"].sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Taxa de absenteismo (base)", f"{taxa_real:.1%}")
    c2.metric("Receita potencial do dia", f"R$ {potencial:,.0f}")
    c3.metric("Perda esperada por faltas", f"R$ {perda:,.0f}")
    c4.metric("AUC-ROC (boosting)",
              f"{modelo['metricas']['gradient_boosting']['auc_roc']:.3f}")

    st.subheader("Desempenho dos modelos (sec. 8.3)")
    met = modelo["metricas"]
    tabela_met = pd.DataFrame({
        "modelo": ["Regressao logistica", "Gradient boosting"],
        "AUC-ROC": [met["regressao_logistica"]["auc_roc"],
                    met["gradient_boosting"]["auc_roc"]],
        "Brier (menor melhor)": [met["regressao_logistica"]["brier"],
                                 met["gradient_boosting"]["brier"]],
    })
    st.dataframe(tabela_met, hide_index=True, use_container_width=True)

    st.subheader("Principais fatores de risco (regressao logistica)")
    coefs = modelo["coeficientes"].head(12).copy()
    fig = px.bar(coefs.sort_values("coeficiente"), x="coeficiente", y="variavel",
                 orientation="h", color="coeficiente",
                 color_continuous_scale="RdBu_r",
                 labels={"coeficiente": "Peso (log-odds)", "variavel": ""})
    fig.update_layout(height=420, coloraxis_showscale=False,
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Peso positivo aumenta o risco de falta; negativo reduz.")


# ===================== ABA 2: RISCO =====================
with aba2:
    st.subheader("Distribuicao por faixa de risco (Tabela 1, sec. 9)")
    cont = (dia["nivel_risco"].value_counts()
            .reindex(["baixo", "medio", "alto", "muito_alto"]).fillna(0).astype(int))

    col_a, col_b = st.columns([1, 1])
    with col_a:
        fig = go.Figure(go.Bar(
            x=cont.index, y=cont.values,
            marker_color=[CORES_RISCO[n] for n in cont.index]))
        fig.update_layout(height=360, yaxis_title="Agendamentos",
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig2 = px.histogram(dia, x="prob_falta", nbins=30,
                            labels={"prob_falta": "Probabilidade de falta"})
        fig2.update_layout(height=360, yaxis_title="Frequencia",
                           margin=dict(l=10, r=10, t=10, b=10))
        for lo, hi, nome, _ in FAIXAS[:-1]:
            fig2.add_vline(x=hi, line_dash="dash", line_color="gray")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Acoes recomendadas por faixa")
    legenda = pd.DataFrame(
        [{"nivel": n, "faixa": f"{lo:.2f} a {hi:.2f}" if hi < 1 else f">= {lo:.2f}",
          "acao": a} for lo, hi, n, a in FAIXAS])
    st.dataframe(legenda, hide_index=True, use_container_width=True)

    st.subheader("Agendamentos escorados")
    filtro = st.multiselect("Filtrar por nivel", list(CORES_RISCO),
                            default=["alto", "muito_alto"])
    cols = ["id_agendamento", "modalidade", "turno", "convenio", "confirmado",
            "antecedencia_dias", "faltas_previas", "prob_falta", "nivel_risco",
            "acao_recomendada"]
    vis = dia[dia["nivel_risco"].isin(filtro)][cols] if filtro else dia[cols]
    st.dataframe(vis, hide_index=True, use_container_width=True, height=300)


# ===================== ABA 3: CONFIRMACOES =====================
with aba3:
    st.subheader("Priorizacao de confirmacao ativa sob orcamento (sec. 11)")
    conf = otimizar_confirmacoes(
        receita=dia["receita_estimada"].values,
        p_falta=dia["prob_falta"].values,
        reducao_relativa=reducao,
        custo_intervencao=custo_int,
        orcamento=float(orcamento))

    c1, c2, c3 = st.columns(3)
    c1.metric("Intervencoes selecionadas", f"{conf['n_intervencoes']} / {len(dia)}")
    c2.metric("Ganho esperado liquido", f"R$ {conf['ganho_esperado']:,.0f}")
    c3.metric("Custo total", f"R$ {conf['custo_total']:,.0f}")

    sel = dia.copy()
    sel["confirmacao_ativa"] = conf["selecionados"]
    sel["ganho_unitario"] = (sel["receita_estimada"] * sel["prob_falta"] * reducao
                             - custo_int).round(2)

    fig = px.scatter(sel, x="prob_falta", y="receita_estimada",
                     color=sel["confirmacao_ativa"].map({1: "Intervir", 0: "Nao intervir"}),
                     color_discrete_map={"Intervir": "#c62828", "Nao intervir": "#90a4ae"},
                     labels={"prob_falta": "Probabilidade de falta",
                             "receita_estimada": "Receita estimada (R$)", "color": ""},
                     hover_data=["modalidade", "ganho_unitario"])
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("A acao prioriza pacientes que combinam alto risco e alta receita, "
               "respeitando o orcamento diario.")

    st.dataframe(
        sel[sel["confirmacao_ativa"] == 1][
            ["id_agendamento", "modalidade", "prob_falta", "receita_estimada",
             "ganho_unitario", "nivel_risco"]].sort_values("ganho_unitario",
                                                            ascending=False),
        hide_index=True, use_container_width=True, height=260)


# ===================== ABA 4: AGENDA =====================
with aba4:
    st.subheader("Otimizacao da alocacao da agenda (PLI, sec. 10)")
    mods = sorted(dia["modalidade"].unique().tolist())
    capacidade = {(t, m): cap_min for t in HORARIOS for m in mods}
    overbooking = {(t, m): ob_min for t in HORARIOS for m in mods}

    with st.spinner("Resolvendo o modelo de otimizacao..."):
        ag = otimizar_agenda(dia, HORARIOS, capacidade, overbooking, lam=lam)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", ag.status)
    c2.metric("Pacientes alocados", f"{len(ag.alocacoes)} / {len(dia)}")
    c3.metric("Receita esperada", f"R$ {ag.receita_esperada:,.0f}")
    c4.metric("Atraso esperado", f"{ag.atraso_total:.0f} min")

    st.subheader("Mapa de ocupacao esperada (min) por horario x modalidade")
    if not ag.ocupacao.empty:
        piv = ag.ocupacao.pivot(index="modalidade", columns="horario",
                                values="ocup_esperada_min").reindex(columns=HORARIOS)
        fig = px.imshow(piv, text_auto=".0f", aspect="auto",
                        color_continuous_scale="YlOrRd",
                        labels=dict(color="min esperados"))
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Ocupacao detalhada por bloco")
    st.dataframe(ag.ocupacao, hide_index=True, use_container_width=True, height=280)

    st.subheader("Alocacoes")
    if not ag.alocacoes.empty:
        det = ag.alocacoes.merge(
            dia[["id_agendamento", "prob_falta", "receita_estimada", "nivel_risco"]],
            on="id_agendamento", how="left")
        st.dataframe(det.sort_values(["horario", "modalidade"]),
                     hide_index=True, use_container_width=True, height=300)
