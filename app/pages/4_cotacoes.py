# Configuração do caminho raiz para localizar o pacote app
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from app.repositories.portfolio_repository import save_fx, latest_fx
from app.services.quote_service import update_quotes

st.header("Cotações e câmbio")
st.write("A atualização consulta o último candle diário disponível no Yahoo Finance para cada ativo ativo cadastrado.")

if st.button("Atualizar cotações agora", type="primary"):
    with st.spinner("Consultando os ativos cadastrados..."):
        results = update_quotes()
    df = pd.DataFrame(results)
    if not df.empty:
        st.dataframe(df, width="stretch", hide_index=True)
        successes = sum(1 for item in results if item["status"] == "sucesso")
        st.success(f"Atualização concluída: {successes} de {len(results)} ativos atualizados.")
        failures = [item for item in results if item["status"] != "sucesso"]
        if failures:
            st.warning(f"{len(failures)} ativo(s) não foram atualizados. Consulte a coluna mensagem.")
    else:
        st.info("Não há ativos ativos para atualizar.")

st.divider()
st.subheader("Taxa de câmbio USD/BRL")
current_fx = latest_fx("USD", "BRL")
if current_fx:
    st.caption(f"Última taxa cadastrada: {float(current_fx['rate']):.6f} — {current_fx['observed_at']}")
else:
    st.info("Ainda não há taxa USD/BRL cadastrada. O consolidado em BRL ficará indisponível.")

with st.form("fx_form"):
    rate = st.number_input("USD/BRL", min_value=0.000001, value=5.0, step=0.01, format="%.6f")
    submitted = st.form_submit_button("Salvar taxa informada")
    if submitted:
        try:
            save_fx(rate, "USD", "BRL")
            st.success("Taxa USD/BRL registrada.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

st.caption("A taxa é informada manualmente pelo usuário. Confira a fonte e a data do câmbio antes de utilizá-la em análises.")
