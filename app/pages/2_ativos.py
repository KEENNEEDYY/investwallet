# Configuração do caminho raiz para localizar o pacote app
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from app.services.asset_service import get_assets, upsert_asset
from app.services.history_service import update_asset_history

st.header("Cadastro de ativos")
with st.form("asset_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    ticker = c1.text_input("Ticker", placeholder="Ex.: PETR4.SA ou AAPL").upper().strip()
    nome = c2.text_input("Nome do ativo")
    c3, c4, c5 = st.columns(3)
    mercado = c3.selectbox("Mercado", ["BR", "US"])
    moeda = c4.selectbox("Moeda", ["BRL", "USD"], index=0 if mercado == "BR" else 1)
    bolsas = ["B3", "Outra"] if mercado == "BR" else ["NASDAQ", "NYSE", "NASDAQ/NYSE", "Outra"]
    bolsa = c5.selectbox("Bolsa", bolsas)
    tipo = st.selectbox("Tipo", ["AÇÃO", "ETF", "BDR", "FII", "REIT", "OUTRO"])
    submitted = st.form_submit_button("Salvar ativo")

    if submitted:
        try:
            upsert_asset(ticker, nome, tipo, mercado, bolsa, moeda)
            st.success(f"Ativo {ticker} salvo.")

            try:
                with st.spinner(f"Carregando histórico de {ticker}..."):
                    resultado = update_asset_history(ticker, mercado)

                st.success(
                    f"Histórico de {ticker} atualizado: "
                    f"{resultado['registros']} registros, "
                    f"de {resultado['primeira_data']} até "
                    f"{resultado['ultima_data']}."
                )

            except Exception as exc:
                st.warning(
                    f"O ativo foi cadastrado, mas o histórico não pôde "
                    f"ser atualizado: {exc}"
                )

        except Exception as exc:
            st.error(str(exc))

assets = get_assets()
st.subheader("Ativos cadastrados")
if assets:
    st.dataframe(pd.DataFrame(assets), width="stretch", hide_index=True)
else:
    st.info("Nenhum ativo cadastrado.")

st.caption("Para ativos brasileiros, use o ticker reconhecido pelo Yahoo Finance, normalmente com sufixo .SA (ex.: PETR4.SA).")
