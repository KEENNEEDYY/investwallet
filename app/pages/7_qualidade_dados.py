
import pandas as pd
import streamlit as st

from app.services.history_quality_service import evaluate_history_quality
from app.services.history_service import reinforce_insufficient_histories


st.title("Qualidade dos Dados")
st.caption(
    "Diagnóstico da cobertura e consistência dos históricos "
    "dos ativos cadastrados."
)

if st.button(
    "🔄 Atualizar históricos insuficientes",
    type="primary",
):
    with st.spinner(
        "Buscando históricos completos e inserindo registros ausentes..."
    ):
        resultados_atualizacao = reinforce_insufficient_histories()

    if resultados_atualizacao:
        df_atualizacao = pd.DataFrame(resultados_atualizacao)
        st.subheader("Resultado da atualização")
        st.dataframe(
            df_atualizacao,
            use_container_width=True,
            hide_index=True,
        )

        erros = [
            item for item in resultados_atualizacao
            if item["status"] == "erro"
        ]

        if erros:
            st.warning(
                f"{len(erros)} ativo(s) apresentaram erros. "
                "Consulte os detalhes na tabela."
            )
        else:
            st.success("Atualização dos históricos concluída.")
    else:
        st.info("Nenhum ativo precisa de reforço no momento.")

if st.button("🔎 Validar todos os ativos", type="primary"):
    st.cache_data.clear()
    st.rerun()

with st.spinner("Analisando os históricos dos ativos..."):
    resultados = evaluate_history_quality()

if not resultados:
    st.info("Nenhum ativo cadastrado para validação.")
    st.stop()

df = pd.DataFrame(resultados)

total = len(df)
adequados = int((df["status"] == "Adequado").sum())
em_formacao = int((df["status"] == "Em formação").sum())
insuficientes = int((df["status"] == "Insuficiente").sum())
sem_historico = int((df["status"] == "Sem histórico").sum())
problemas = int((df["status"] == "Com problemas").sum())

st.subheader("Visão geral")

col1, col2, col3 = st.columns(3)
col1.metric("Ativos cadastrados", total)
col2.metric("Adequados", adequados)
col3.metric("Em formação", em_formacao)

col4, col5, col6 = st.columns(3)
col4.metric("Insuficientes", insuficientes)
col5.metric("Sem histórico", sem_historico)
col6.metric("Com problemas", problemas)

st.divider()

st.subheader("Detalhamento por ativo")

classificacoes = [
    "Todos",
    "Adequado",
    "Em Formação",
    "Insuficiente",
    "Sem histórico",
    "Com problemas",
]

filtro = st.selectbox(
    "Filtrar por classificação",
    classificacoes,
)

df_exibicao = df.copy()

if filtro != "Todos":
    df_exibicao = df_exibicao[
        df_exibicao["status"] == filtro
    ]

colunas = [
    "ticker",
    "nome",
    "mercado",
    "total_registros",
    "primeira_data",
    "ultima_data",
    "registros_invalidos",
    "percentual_invalido",
    "status",
]

df_exibicao = df_exibicao[colunas].rename(
    columns={
        "ticker": "Ticker",
        "nome": "Nome",
        "mercado": "Mercado",
        "total_registros": "Registros",
        "primeira_data": "Primeira data",
        "ultima_data": "Última data",
        "registros_invalidos": "Inválidos",
        "percentual_invalido": "% inválido",
        "status": "Classificação",
    }
)

st.dataframe(
    df_exibicao,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Critérios operacionais: menos de 60 registros = Insuficiente; "
    "60 a 119 = Básico; 120 ou mais = Adequado. "
    "Inconsistências relevantes são classificadas como Com problemas."
)
