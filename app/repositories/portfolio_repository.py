import math

from app.database.connection import connect


def list_positions():
    with connect() as conn:
        rows = conn.execute("""
            SELECT
                c.ticker,
                c.quantidade,
                c.preco_medio,
                COALESCE(a.nome, c.ticker) AS nome,
                a.mercado,
                COALESCE(q.moeda, a.moeda) AS moeda,
                q.preco AS preco_atual,
                q.data_hora AS cotacao_em
            FROM carteira c
            LEFT JOIN ativos a ON a.ticker = c.ticker
            LEFT JOIN cotacoes q ON q.id = (
                SELECT q2.id FROM cotacoes q2
                WHERE q2.ticker = c.ticker
                ORDER BY q2.data_hora DESC, q2.id DESC LIMIT 1
            )
            ORDER BY c.ticker
        """).fetchall()
        return [dict(row) for row in rows]


def latest_fx(base="USD", quote="BRL"):
    with connect() as conn:
        row = conn.execute("""
            SELECT rate, observed_at FROM fx_rates
            WHERE base_currency = ? AND quote_currency = ?
            ORDER BY observed_at DESC, id DESC LIMIT 1
        """, (base, quote)).fetchone()
        return dict(row) if row else None


def save_fx(rate, base="USD", quote="BRL", observed_at=None):
    rate = float(rate)
    if not math.isfinite(rate) or rate <= 0:
        raise ValueError("A taxa de câmbio deve ser um número positivo.")
    with connect() as conn:
        conn.execute("""
            INSERT INTO fx_rates(base_currency, quote_currency, rate, observed_at)
            VALUES (?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
        """, (base, quote, rate, observed_at))


def list_assets(active_only=False):
    query = "SELECT ticker,nome,tipo,ativo,mercado,bolsa,moeda FROM ativos"
    if active_only:
        query += " WHERE ativo = 1"
    query += " ORDER BY ticker"
    with connect() as conn:
        return [dict(row) for row in conn.execute(query)]


def save_asset(ticker, nome, tipo, mercado, bolsa, moeda):
    with connect() as conn:
        conn.execute("""
            INSERT INTO ativos(ticker,nome,tipo,ativo,mercado,bolsa,moeda)
            VALUES(?,?,?,1,?,?,?)
            ON CONFLICT(ticker) DO UPDATE SET
                nome=excluded.nome, tipo=excluded.tipo, ativo=1,
                mercado=excluded.mercado, bolsa=excluded.bolsa, moeda=excluded.moeda
        """, (ticker.upper().strip(), nome, tipo, mercado, bolsa, moeda))


def insert_quote(ticker, price, currency, low=None, high=None, open_price=None,
                 previous_close=None, change=None, change_percent=None, observed_at=None):
    with connect() as conn:
        conn.execute("""
            INSERT INTO cotacoes(
                ticker, preco, minima_dia, maxima_dia, abertura,
                fechamento_anterior, variacao, variacao_percentual, data_hora, moeda
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), ?)
        """, (ticker, price, low, high, open_price, previous_close,
              change, change_percent, observed_at, currency))


def list_movements(limit=200):
    with connect() as conn:
        rows = conn.execute("""
            SELECT id, ticker, tipo, quantidade, preco, data_operacao
            FROM movimentacoes ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]
