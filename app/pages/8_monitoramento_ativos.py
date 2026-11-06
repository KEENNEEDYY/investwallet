from pathlib import Path
import sys
import html

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.repositories.portfolio_repository import list_assets

from app.services.monitoring_runtime import (
    get_shared_monitoring_service,
    refresh_shared_monitoring_symbols,
)

from app.config import MONITORING_REFRESH_SECONDS


st.set_page_config(
    page_title="Monitoramento",
    page_icon="📡",
    layout="wide"
)


st.title("📡 Monitoramento de todos os ativos")
st.caption("Acompanhamento estatístico de todos os ativos cadastrados e ativos.")

try:
    collector, service = get_shared_monitoring_service()
except ValueError as error:
    st.error(str(error))
    st.stop()


@st.fragment(run_every=f"{MONITORING_REFRESH_SECONDS}s")
def render_monitoring():

    assets = list_assets(active_only=True)

    symbols = [
        asset["ticker"]
        for asset in assets
    ]

    refresh_shared_monitoring_symbols(collector)

    if not symbols:
        st.info(
            "Nenhum ativo ativo cadastrado. "
            "Cadastre ou ative ativos na página Ativos."
        )
        return

    if collector.is_connected():
        st.success("Conectado à Finnhub")
    else:
        st.warning("Aguardando conexão com a Finnhub")

    data = service.get_monitoring_data(period_days=365)

    if not data:
        st.info(
            "Aguardando cotações dos ativos cadastrados. "
            "Verifique a conexão e as permissões da API."
        )
        return


    st.subheader("Filtros do monitoramento")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        percentil_minimo = st.slider(
            "Percentil mínimo",
            min_value=0,
            max_value=100,
            value=0,
            step=1
        )

    with filter_col2:
        status_selecionados = st.multiselect(
            "Status do alerta",
            options=[
                "NORMAL",
                "ATENÇÃO",
                "EXTREMO",
                "MUITO EXTREMO"
            ],
            default=["EXTREMO", "MUITO EXTREMO", "ATENÇÃO"]
        )

    with filter_col3:
        tickers_disponiveis = sorted(
            item["ticker"] for item in data
        )

        tickers_selecionados = st.multiselect(
            "Ativos",
            options=tickers_disponiveis,
            default=[]
        )

        variacoes_selecionadas = st.multiselect(
            "Direção da variação percentual",
            options=[
                "POSITIVA (> 0%)",
                "NEGATIVA (< 0%)"
            ],
            default=[],
            help=(
                "Selecione se deseja filtrar variações positivas "
                "ou negativas. Sem seleção, não aplica esse critério."
            )
        )    

    criterio = st.radio(
        "Combinar filtros de percentil e status",
        options=["E", "OU"],
        horizontal=True,
        help=(
            "OU: atende ao percentil mínimo ou a um dos status. "
            "E: precisa atender aos dois critérios."
        )
    )

    filtrados = []

    for item in data:
        atende_percentil = (
            item["percentil"] >= percentil_minimo
        )

        atende_status = (
            item["alerta"] in status_selecionados
        )

        variacao = item["variacao_percentual"]

        atende_variacao = (
            (
                "POSITIVA (> 0%)" in variacoes_selecionadas
                and variacao > 0
            )
            or
            (
                "NEGATIVA (< 0%)" in variacoes_selecionadas
                and variacao < 0
            )
        )

        criterios = [atende_percentil]

        if status_selecionados:
            criterios.append(atende_status)

        if variacoes_selecionadas:
            criterios.append(atende_variacao)

        if criterio == "OU":
            atende_criterios = any(criterios)
        else:
            atende_criterios = all(criterios)

        atende_ticker = (
            not tickers_selecionados
            or item["ticker"] in tickers_selecionados
        )

        if atende_criterios and atende_ticker:
            filtrados.append(item)

    st.caption(
        f"Exibindo {len(filtrados)} de {len(data)} ativos."
    )

    if not filtrados:
        st.info("Nenhum ativo atende aos filtros selecionados.")
        return




    colors = {
        "NORMAL": "#198754",
        "ATENÇÃO": "#d6a000",
        "EXTREMO": "#fd7e14",
        "MUITO EXTREMO": "#dc3545",
    }

    st.subheader("Mapa de calor dos ativos")

    columns = st.columns(2)

    for index, item in enumerate(filtrados):
        ticker = html.escape(item["ticker"])
        color = colors[item["alerta"]]

        with columns[index % 2]:
            with st.container(border=True):
                st.subheader(ticker)

                st.metric(
                    "Cotação atual",
                    f"{item['preco']:,.2f}",
                    f"{item['variacao_percentual']:+.2f}%"
                )

                st.markdown(
                    f"""
                    <div style="
                        background:{color};
                        color:white;
                        padding:10px;
                        border-radius:8px;
                        text-align:center;
                        font-weight:bold;">
                        {item['alerta']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write(f"**Z-score:** {item['z_score']:.2f}")
                st.write(f"**Percentil:** {item['percentil']:.2f}%")
                st.write(
                    f"**Média histórica:** "
                    f"{item['media_historica']:.4f}%"
                )
                st.write(
                    f"**Desvio padrão:** "
                    f"{item['desvio_padrao']:.4f}%"
                )


render_monitoring()