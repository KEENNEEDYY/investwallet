# Configuração do caminho raiz
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st
import altair as alt

from app.services.analytics_service import (
    available_tickers,
    ticker_analytics,
)


st.header("Analytics histórico")

tickers = available_tickers()

if not tickers:
    st.info("Não há histórico diário cadastrado.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    ticker = st.selectbox("Ativo", tickers)

with col2:
    period_label = st.selectbox(
        "Período de análise",
        ["30 dias", "90 dias", "180 dias", "365 dias", "Todo o histórico"],
        index=3,
    )

period_map = {
    "30 dias": 30,
    "90 dias": 90,
    "180 dias": 180,
    "365 dias": 365,
    "Todo o histórico": None,
}

data = ticker_analytics(
    ticker,
    period_days=period_map[period_label],
)

stats = data["statistics"]
history = pd.DataFrame(data["history"])

st.caption(
    f"{data['samples']} retornos diários calculados para {ticker}."
)

if history.empty:
    st.warning("Não há dados disponíveis para o período selecionado.")
    st.stop()

history["data_pregao"] = pd.to_datetime(history["data_pregao"])

# Histórico de fechamento
st.subheader("Histórico de fechamento")

st.line_chart(
    history.set_index("data_pregao")["fechamento"]
)

# Retornos diários
st.subheader("Retornos diários (%)")

returns_history = history.dropna(
    subset=["variacao_percentual"]
)

st.line_chart(
    returns_history.set_index("data_pregao")[
        "variacao_percentual"
    ]
)

if not stats:
    st.warning("Não há observações suficientes para as estatísticas.")
    st.stop()

# Indicadores
st.subheader("Indicadores estatísticos")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Média diária", f"{stats['media']:.4f}%")
c2.metric("Desvio-padrão", f"{stats['desvio_padrao']:.4f}%")
c3.metric("Último retorno", f"{stats['retorno_mais_recente']:.4f}%")
c4.metric("Z-score", f"{stats['z_score']:.2f}")

st.write(
    f"Percentil empírico do último retorno: "
    f"**{stats['percentil']:.2f}%**"
)

# Histograma e curva normal
st.subheader("Histograma e curva de Gauss")

histogram = pd.DataFrame(data["histogram"])

if not histogram.empty:
    chart = alt.Chart(histogram).encode(
        x=alt.X(
            "centro:Q",
            title="Retorno diário (%)",
            axis=alt.Axis(format=".2f"),
        ),
        tooltip=[
            alt.Tooltip("faixa:N", title="Faixa"),
            alt.Tooltip("frequencia:Q", title="Ocorrências"),
            alt.Tooltip("percentual:Q", title="Frequência (%)", format=".2f"),
            alt.Tooltip("gauss_percentual:Q", title="Gauss (%)", format=".2f"),
        ],
    )

    bars = chart.mark_bar(opacity=0.65).encode(
        y=alt.Y(
            "percentual:Q",
            title="Frequência relativa (%)",
        )
    )

    gaussian = chart.mark_line(
        color="red",
        strokeWidth=2.5,
        point=True,
    ).encode(
        y="gauss_percentual:Q"
    )

    st.altair_chart(
        bars + gaussian,
        use_container_width=True,
    )

    st.caption(
        "Barras: frequência relativa observada. "
        "Linha: probabilidade teórica por faixa segundo a distribuição normal."
    )

    st.subheader("Tabela de frequências")

    display_histogram = histogram[
        ["faixa", "frequencia", "percentual", "gauss_percentual"]
    ].copy()

    display_histogram.columns = [
        "Faixa de retorno",
        "Frequência absoluta",
        "Frequência relativa (%)",
        "Gauss teórica (%)",
    ]

    st.dataframe(
        display_histogram.style.format({
            "Frequência relativa (%)": "{:.2f}",
            "Gauss teórica (%)": "{:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

# Faixas sigma
st.subheader("Faixas estatísticas")

sigma_data = []

for label, bounds in stats["faixas"].items():
    sigma_data.append({
        "Faixa": label.replace("_", " ").upper(),
        "Limite inferior (%)": bounds[0],
        "Limite superior (%)": bounds[1],
    })

st.dataframe(
    pd.DataFrame(sigma_data).style.format({
        "Limite inferior (%)": "{:.4f}",
        "Limite superior (%)": "{:.4f}",
    }),
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Estatísticas descritivas históricas. A distribuição normal é uma "
    "aproximação teórica e não representa previsão ou recomendação de investimento."
)

# Eventos extremos
st.subheader("Detecção de eventos extremos")

extremes = data.get("extremes")

if extremes:
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Eventos ≥ 2 sigmas",
        extremes["total_2_sigma"],
        f"{extremes['percentual_2_sigma']:.2f}% da amostra",
    )

    c2.metric(
        "Eventos ≥ 3 sigmas",
        extremes["total_3_sigma"],
        f"{extremes['percentual_3_sigma']:.2f}% da amostra",
    )

    c3.metric(
        "Observações analisadas",
        extremes["total_observacoes"],
    )

    st.markdown("**Frequência observada versus referência normal**")

    comparison = pd.DataFrame([
        {
            "Limite": "±2 sigmas",
            "Observado (%)": extremes["percentual_2_sigma"],
            "Esperado pela normal (%)": extremes["esperado_2_sigma"],
        },
        {
            "Limite": "±3 sigmas",
            "Observado (%)": extremes["percentual_3_sigma"],
            "Esperado pela normal (%)": extremes["esperado_3_sigma"],
        },
    ])

    st.dataframe(
        comparison.style.format({
            "Observado (%)": "{:.3f}",
            "Esperado pela normal (%)": "{:.3f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("**Histórico de eventos extremos**")

    if extremes["eventos"]:
        events_df = pd.DataFrame(extremes["eventos"])

        events_df.columns = [
            "Data",
            "Retorno diário (%)",
            "Z-score",
            "Classificação",
            "Direção",
        ]

        st.dataframe(
            events_df.style.format({
                "Retorno diário (%)": "{:.3f}",
                "Z-score": "{:.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success(
            "Nenhum evento acima de 2 desvios-padrão "
            "foi identificado no período."
        )

    st.caption(
        "A classificação é baseada na média e no desvio-padrão "
        "da amostra selecionada. Eventos extremos não significam "
        "necessariamente erro ou oportunidade de investimento."
    )