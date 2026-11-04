from app.database.connection import connect


def save_daily_history(records):
    """
    Insere ou atualiza candles diários.
    A chave ticker + data_pregao impede duplicações.
    """
    if not records:
        return 0

    with connect() as conn:
        conn.executemany("""
            INSERT INTO historico_diario (
                ticker,
                data_pregao,
                abertura,
                maxima,
                minima,
                fechamento,
                variacao_percentual,
                volume
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, data_pregao) DO UPDATE SET
                abertura = excluded.abertura,
                maxima = excluded.maxima,
                minima = excluded.minima,
                fechamento = excluded.fechamento,
                variacao_percentual = excluded.variacao_percentual,
                volume = excluded.volume
        """, records)

    return len(records)



def get_latest_history_date(ticker):
    """Retorna a última data de histórico diário gravada para o ativo."""
    with connect() as conn:
        row = conn.execute("""
            SELECT MAX(data_pregao) AS ultima_data
            FROM historico_diario
            WHERE ticker = ?
        """, (ticker,)).fetchone()

    return row["ultima_data"] if row else None


def insert_missing_daily_history(records):
    """
    Insere somente candles ainda inexistentes.
    Registros já cadastrados não são alterados.
    """
    if not records:
        return 0

    with connect() as conn:
        cursor = conn.executemany("""
            INSERT INTO historico_diario (
                ticker,
                data_pregao,
                abertura,
                maxima,
                minima,
                fechamento,
                variacao_percentual,
                volume
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, data_pregao) DO NOTHING
        """, records)

    return cursor.rowcount