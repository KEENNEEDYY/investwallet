import math
from app.database.connection import connect


def register_movement(ticker, operation, quantity, price, operation_date=None):
    ticker = (ticker or "").strip().upper()
    operation = (operation or "").strip().upper()
    quantity = float(quantity)
    price = float(price)
    if not ticker:
        raise ValueError("Informe o ticker.")
    if operation not in ("COMPRA", "VENDA"):
        raise ValueError("Operação deve ser COMPRA ou VENDA.")
    if not math.isfinite(quantity) or quantity <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")
    if not math.isfinite(price) or price <= 0:
        raise ValueError("O preço deve ser maior que zero.")

    with connect() as conn:
        asset = conn.execute("SELECT ticker FROM ativos WHERE ticker=? AND ativo=1", (ticker,)).fetchone()
        if asset is None:
            raise ValueError(f"O ativo {ticker} não está cadastrado ou está inativo.")

        current = conn.execute(
            "SELECT quantidade FROM carteira WHERE ticker=?", (ticker,)
        ).fetchone()
        current_quantity = float(current["quantidade"]) if current else 0.0
        if operation == "VENDA" and quantity > current_quantity + 1e-9:
            raise ValueError(
                f"Quantidade insuficiente para venda. Disponível: {current_quantity:g}."
            )

        if operation_date:
            conn.execute("""
                INSERT INTO movimentacoes(ticker,tipo,quantidade,preco,data_operacao)
                VALUES(?,?,?,?,?)
            """, (ticker, operation, quantity, price, operation_date))
        else:
            conn.execute("""
                INSERT INTO movimentacoes(ticker,tipo,quantidade,preco)
                VALUES(?,?,?,?)
            """, (ticker, operation, quantity, price))

        rows = conn.execute("""
            SELECT tipo, quantidade, preco FROM movimentacoes
            WHERE ticker=? ORDER BY id
        """, (ticker,)).fetchall()
        qty = 0.0
        cost = 0.0
        for row in rows:
            q = float(row["quantidade"])
            p = float(row["preco"])
            if row["tipo"].upper() == "COMPRA":
                qty += q
                cost += q * p
            elif row["tipo"].upper() == "VENDA":
                if q > qty + 1e-8:
                    raise ValueError("O histórico de movimentações contém venda superior à posição disponível.")
                average = cost / qty if qty > 0 else 0.0
                qty -= q
                cost = average * qty
        if qty <= 1e-8:
            conn.execute("DELETE FROM carteira WHERE ticker=?", (ticker,))
        else:
            average = cost / qty
            conn.execute("""
                INSERT INTO carteira(ticker,quantidade,preco_medio)
                VALUES(?,?,?)
                ON CONFLICT(ticker) DO UPDATE SET
                    quantidade=excluded.quantidade, preco_medio=excluded.preco_medio
            """, (ticker, qty, average))


def get_movements(limit=200):
    with connect() as conn:
        rows = conn.execute("""
            SELECT m.id,m.ticker,m.tipo,m.quantidade,m.preco,m.data_operacao,
                   COALESCE(a.moeda,'') AS moeda
            FROM movimentacoes m LEFT JOIN ativos a ON a.ticker=m.ticker
            ORDER BY m.id DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]
