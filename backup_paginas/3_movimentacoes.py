import pandas as pd
import streamlit as st

from app.services.asset_service import get_assets
from app.services.movement_service import get_movements, register_movement

st.header("Movimentações")
assets = [a for a in get_assets(active_only=True)]
asset_tickers = [a["ticker"] for a in assets]

if not asset_tickers:
    st.info("Cadastre um ativo antes de registrar uma movimentação.")
else:
    with st.form("movement_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        ticker = c1.selectbox("Ativo", asset_tickers)
        operation = c2.selectbox("Operação", ["COMPRA", "VENDA"])
        quantity = c3.number_input("Quantidade", min_value=0.00000001, value=1.0, format="%.8f")
        price = st.number_input("Preço unitário na moeda do ativo", min_value=0.00000001, value=1.0, format="%.6f")
        submitted = st.form_submit_button("Registrar movimentação")
        if submitted:
            try:
                register_movement(ticker, operation, quantity, price)
                st.success("Movimentação registrada e carteira recalculada.")
            except Exception as exc:
                st.error(str(exc))

st.subheader("Histórico recente")
movements = get_movements()
if movements:
    st.dataframe(pd.DataFrame(movements), width="stretch", hide_index=True)
else:
    st.info("Nenhuma movimentação encontrada.")
