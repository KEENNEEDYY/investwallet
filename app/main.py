
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.database.connection import initialize_database
from app.services.history_service import update_historical_quotes


@st.cache_resource(show_spinner=False)
def startup_history_update():
    """Executa a atualização uma vez por processo do Streamlit."""
    return update_historical_quotes()


st.set_page_config(page_title="InvestWallet", page_icon="📈", layout="wide")

initialize_database()

st.title("InvestWallet")
st.caption("Gestão de carteira e analytics — Brasil 🇧🇷 | Estados Unidos 🇺🇸")

with st.spinner("Atualizando histórico diário dos ativos..."):
    history_results = startup_history_update()

if history_results:
    sucessos = sum(
        1 for result in history_results
        if result["status"] == "sucesso"
    )
    erros = [
        result for result in history_results
        if result["status"] == "erro"
    ]

    with st.expander(
        f"Atualização do histórico: {sucessos} sucesso(s), {len(erros)} erro(s)"
    ):
        st.dataframe(history_results, use_container_width=True)

        if erros:
            st.warning(
                "Alguns ativos não tiveram o histórico atualizado. "
                "Consulte os detalhes na tabela acima."
            )

pages = [
    st.Page("pages/1_dashboard.py", title="Dashboard", icon="📊", default=True),
    st.Page("pages/2_ativos.py", title="Ativos", icon="🧾"),
    st.Page("pages/3_movimentacoes.py", title="Movimentações", icon="💼"),
    st.Page("pages/4_cotacoes.py", title="Cotações e câmbio", icon="💱"),
    st.Page("pages/5_analytics.py", title="Analytics", icon="📈"),
    st.Page("pages/6_monitoramento.py", title="Monitoramento", icon="📡"),
    st.Page("pages/7_qualidade_dados.py", title="Qualidade dos Dados", icon="🧪"),
]

st.navigation(pages).run()
