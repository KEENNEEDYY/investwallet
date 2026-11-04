from app.database import (
    get_connection,
    atualizar_snapshot
)
from app.database import inserir_resumo


def atualizar_portfolio():

    atualizar_portfolio_snapshot()

    atualizar_portfolio_resumo()

def atualizar_portfolio_snapshot():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE * FROM portfolio_snapshot
        """)

    query = """
    SELECT

        c.ticker,
        c.quantidade,
        c.preco_medio,

        ct.preco,

        c.quantidade * c.preco_medio
            AS valor_investido,

        c.quantidade * ct.preco
            AS valor_atual,

        (
            (ct.preco - c.preco_medio)
            * c.quantidade
        ) AS lucro,

        (
            (
                ct.preco
                / c.preco_medio
            ) - 1
        ) * 100
            AS rentabilidade

    FROM carteira c

    JOIN (

        SELECT
            ticker,
            MAX(id) AS id

        FROM cotacoes

        GROUP BY ticker

    ) ultima

    ON c.ticker = ultima.ticker

    JOIN cotacoes ct

    ON ct.id = ultima.id
    """

    cursor.execute(query)

    dados = cursor.fetchall()

    conn.close()

    for linha in dados:

        (
            ticker,
            quantidade,
            preco_medio,
            preco_atual,
            valor_investido,
            valor_atual,
            lucro,
            rentabilidade
        ) = linha

        atualizar_snapshot(
            ticker=ticker,
            quantidade=quantidade,
            preco_medio=preco_medio,
            preco_atual=preco_atual,
            valor_investido=valor_investido,
            valor_atual=valor_atual,
            lucro=lucro,
            rentabilidade=rentabilidade
        )

def atualizar_portfolio_resumo():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            SUM(valor_investido),

            SUM(valor_atual),

            SUM(lucro)

        FROM portfolio_snapshot

    """)

    resultado = cursor.fetchone()

    conn.close()

    total_investido = resultado[0] or 0

    patrimonio_atual = resultado[1] or 0

    lucro_total = resultado[2] or 0

    if total_investido > 0:

        rentabilidade_total = (
            lucro_total
            / total_investido
        ) * 100

    else:

        rentabilidade_total = 0

    inserir_resumo(
        total_investido=round(total_investido, 2),
        patrimonio_atual=round(patrimonio_atual, 2),
        lucro_total=round(lucro_total, 2),
        rentabilidade_total=round(rentabilidade_total, 2)
    )

def main():

    atualizar_portfolio_snapshot()

    atualizar_portfolio_resumo()

    print(
        "Snapshot atualizado."
    )


if __name__ == "__main__":
    main()