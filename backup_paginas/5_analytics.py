import pandas as pd
import streamlit as st

from app.services.analytics_service import available_tickers, ticker_analytics

st.header("Analytics histórico")
tickers = available_tickers()
if not tickers:
    st.info("Não há histórico diário cadastrado. A carga histórica será adicionada à rotina de coleta em uma próxima etapa.")
else:
    ticker = st.selectbox("Ativo", tickers)
    data = ticker_analytics(ticker)
    stats = data["statistics"]
    history = pd.DataFrame(data["history"])
    st.caption(f"{data['samples']} observações históricas para {ticker}.")
    if not history.empty:
        history["data_pregao"] = pd.to_datetime(history["data_pregao"])
        st.subheader("Histórico de fechamento")
        st.line_chart(history.set_index("data_pregao")["fechamento"])
        st.subheader("Distribuição dos retornos diários registrados")
        st.bar_chart(history["variacao_percentual"].round().value_counts().sort_index())
    if stats:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média diária", f"{stats['media']:.3f}%")
        c2.metric("Desvio-padrão", f"{stats['desvio_padrao']:.3f}%")
        c3.metric("Último retorno", f"{stats['retorno_mais_recente']:.3f}%")
        c4.metric("Z-score", f"{stats['z_score']:.2f}")
        st.write(f"Percentil empírico do último retorno: **{stats['percentil']:.1f}%**")
        st.write("Faixas estatísticas calculadas a partir da série disponível:")
        st.json({key: [round(value, 4) for value in bounds] for key, bounds in stats["faixas"].items()})
        st.caption("Estatísticas descritivas históricas; não são previsões nem recomendações de investimento.")
