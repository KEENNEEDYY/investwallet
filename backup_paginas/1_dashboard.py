import pandas as pd
import streamlit as st

from app.services.portfolio_service import dashboard_data

st.header("Visão consolidada")
data = dashboard_data()
totals = data["totals"]
combined = data["combined_brl"]

col1, col2, col3 = st.columns(3)
for col, currency, label, symbol in (
    (col1, "BRL", "Patrimônio Brasil", "R$"),
    (col2, "USD", "Patrimônio EUA", "US$"),
):
    total = totals[currency]
    if total["atual"] is None:
        col.metric(label, "Incompleto")
        col.caption(f"Cotações disponíveis: {total['cotacoes_ok']}/{total['posicoes']}")
    else:
        col.metric(label, f"{symbol} {total['atual']:,.2f}")
        col.caption(f"{total['posicoes']} posição(ões) com cotação")

if combined is None:
    col3.metric("Consolidado em BRL", "Indisponível")
    col3.caption("Cadastre uma taxa USD/BRL e confira as moedas dos ativos.")
elif combined["atual_brl"] is None:
    col3.metric("Consolidado em BRL", "Incompleto")
    col3.caption(f"Câmbio USD/BRL: {data['usd_brl']:.4f}; faltam cotações.")
else:
    col3.metric("Patrimônio consolidado", f"R$ {combined['atual_brl']:,.2f}")
    col3.caption(f"Câmbio USD/BRL: {data['usd_brl']:.4f} em {data['fx_timestamp']}")

st.divider()
if data["missing_quotes"]:
    st.warning(
        "Não há cotação registrada para: " + ", ".join(data["missing_quotes"])
        + ". Os totais de patrimônio foram ocultados para evitar apresentar valores parciais como totais completos."
    )
if data["unknown_currency"]:
    st.error("Moeda não configurada para: " + ", ".join(data["unknown_currency"]))

st.subheader("Posições")
if data["positions"]:
    df = pd.DataFrame(data["positions"])
    columns = [
        "ticker", "nome", "mercado", "moeda", "quantidade", "preco_medio",
        "preco_atual", "valor_investido", "valor_atual", "lucro", "rentabilidade",
    ]
    st.dataframe(df[columns], width="stretch", hide_index=True)
else:
    st.info("Ainda não há posições na carteira. Registre uma compra na página Movimentações.")

st.caption("Os preços são exibidos na moeda nativa. A conversão para BRL depende da taxa USD/BRL cadastrada.")
