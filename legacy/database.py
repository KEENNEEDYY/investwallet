# app/database.py

import sqlite3
from app.config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def listar_movimentacoes():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            ticker,
            tipo,
            quantidade,
            preco,
            data_operacao
        FROM movimentacoes
        ORDER BY id DESC
    """)

    dados = cursor.fetchall()

    conn.close()

    return dados

def listar_carteira():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ticker,
            quantidade,
            ROUND(preco_medio, 2)
        FROM carteira
        ORDER BY ticker
    """)

    dados = cursor.fetchall()

    conn.close()

    return dados

def atualizar_carteira():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM carteira
    """)

    cursor.execute("""
        SELECT DISTINCT ticker
        FROM movimentacoes
    """)

    tickers = [
        row[0]
        for row in cursor.fetchall()
    ]

    for ticker in tickers:

        cursor.execute("""

            SELECT

                tipo,
                quantidade,
                preco

            FROM movimentacoes

            WHERE ticker = ?

            ORDER BY id

        """, (
            ticker,
        ))

        operacoes = cursor.fetchall()

        quantidade_total = 0

        preco_medio = 0

        for (
            tipo,
            quantidade,
            preco
        ) in operacoes:

            if tipo == "COMPRA":

                valor_antigo = (
                    quantidade_total
                    * preco_medio
                )

                valor_novo = (
                    quantidade
                    * preco
                )

                quantidade_total += quantidade

                preco_medio = (
                    valor_antigo +
                    valor_novo
                ) / quantidade_total

            elif tipo == "VENDA":

                quantidade_total -= quantidade

                if quantidade_total < 0:

                    quantidade_total = 0

        if quantidade_total > 0:

            cursor.execute("""

                INSERT INTO carteira(

                    ticker,
                    quantidade,
                    preco_medio

                )

                VALUES(

                    ?, ?, ?

                )

            """, (

                ticker,

                quantidade_total,

                preco_medio

            ))

    conn.commit()

    conn.close()

def listar_movimentacoes():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            id,
            ticker,
            tipo,
            quantidade,
            preco,
            data_operacao

        FROM movimentacoes

        ORDER BY id DESC

    """)

    dados = cursor.fetchall()

    conn.close()

    return dados

def registrar_movimentacao(
    ticker,
    tipo,
    quantidade,
    preco
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movimentacoes(
            ticker,
            tipo,
            quantidade,
            preco
        )
        VALUES(
            ?, ?, ?, ?
        )
    """, (
        ticker,
        tipo,
        quantidade,
        preco
    ))

    conn.commit()

    conn.close()

def obter_ativos():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticker

        FROM ativos

        WHERE ativo = 1
    """)

    dados = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return dados

def excluir_ativo(
    ticker
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ativos
        SET ativo = 0
        WHERE ticker = ?
    """, (
        ticker.upper(),
    ))

    conn.commit()

    conn.close()

def listar_ativos():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ticker,
            nome,
            tipo,
            ativo
        FROM ativos
        ORDER BY ticker
    """)

    dados = cursor.fetchall()

    conn.close()

    return dados

def inserir_ativo(
    ticker,
    nome,
    tipo
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO ativos(
            ticker,
            nome,
            tipo,
            ativo
        )
        VALUES(
            ?, ?, ?, 1
        )
    """, (
        ticker.upper(),
        nome,
        tipo
    ))

    conn.commit()

    conn.close()

def limpar_gauss(ticker):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM gauss_curve
        WHERE ticker = ?
    """, (
        ticker,
    ))

    conn.commit()
    conn.close()

def limpar_histograma(ticker):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM histograma_retorno
        WHERE ticker = ?
    """, (
        ticker,
    ))

    conn.commit()
    conn.close()

def salvar_ponto_gauss(
    ticker,
    retorno,
    densidade
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO gauss_curve(
            ticker,
            retorno,
            densidade
        )
        VALUES(
            ?, ?, ?
        )
    """, (
        ticker,
        retorno,
        densidade
    ))

    conn.commit()

    conn.close()

def salvar_estatistica(
    ticker,
    media_retorno,
    desvio_padrao,
    retorno_atual,
    z_score,
    percentil,
    faixa_1_sigma_inf,
    faixa_1_sigma_sup,
    faixa_2_sigma_inf,
    faixa_2_sigma_sup,
    faixa_3_sigma_inf,
    faixa_3_sigma_sup
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO analytics_estatistica (

            ticker,

            media_retorno,
            desvio_padrao,

            retorno_atual,

            z_score,
            percentil,

            faixa_1_sigma_inf,
            faixa_1_sigma_sup,

            faixa_2_sigma_inf,
            faixa_2_sigma_sup,

            faixa_3_sigma_inf,
            faixa_3_sigma_sup,

            data_calculo

        )
        VALUES (

            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            CURRENT_TIMESTAMP

        )
    """, (

        ticker,

        media_retorno,
        desvio_padrao,

        retorno_atual,

        z_score,
        percentil,

        faixa_1_sigma_inf,
        faixa_1_sigma_sup,

        faixa_2_sigma_inf,
        faixa_2_sigma_sup,

        faixa_3_sigma_inf,
        faixa_3_sigma_sup

    ))

    conn.commit()

    conn.close()

def inserir_resumo(
    total_investido,
    patrimonio_atual,
    lucro_total,
    rentabilidade_total
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO portfolio_resumo(

            total_investido,
            patrimonio_atual,
            lucro_total,
            rentabilidade_total

        )
        VALUES (?, ?, ?, ?)
    """, (
        total_investido,
        patrimonio_atual,
        lucro_total,
        rentabilidade_total
    ))

    conn.commit()

    conn.close()

def atualizar_snapshot(
    ticker,
    quantidade,
    preco_medio,
    preco_atual,
    valor_investido,
    valor_atual,
    lucro,
    rentabilidade
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO portfolio_snapshot(
            ticker,
            quantidade,
            preco_medio,
            preco_atual,
            valor_investido,
            valor_atual,
            lucro,
            rentabilidade,
            ultima_atualizacao
        )
        VALUES(
            ?, ?, ?, ?, ?, ?, ?, ?,
            CURRENT_TIMESTAMP
        )
    """, (
        ticker,
        quantidade,
        preco_medio,
        preco_atual,
        valor_investido,
        valor_atual,
        lucro,
        rentabilidade
    ))

    conn.commit()
    conn.close()

def insert_historico(
        ticker,
        data_pregao,
        abertura,
        maxima,
        minima,
        fechamento,
        variacao_percentual,
        volume
):


    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO historico_diario (
            ticker,
            data_pregao,
            abertura,
            maxima,
            minima,
            fechamento,
            variacao_percentual,
            volume
        )
        VALUES (?,?,?,?,?,?,?,?)
    """,(
        ticker,
        data_pregao,
        abertura,
        maxima,
        minima,
        fechamento,
        variacao_percentual,
        volume
    ))

    conn.commit()
    conn.close()

def insert_quote(
    ticker,
    preco,
    minima,
    maxima,
    abertura,
    fechamento_anterior,
    variacao,
    variacao_percentual
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cotacoes (
            ticker,
            preco,
            minima_dia,
            maxima_dia,
            abertura,
            fechamento_anterior,
            variacao,
            variacao_percentual
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker,
            preco,
            minima,
            maxima,
            abertura,
            fechamento_anterior,
            variacao,
            variacao_percentual
        ))

    conn.commit()
    conn.close()