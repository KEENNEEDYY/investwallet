import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.config import DB_PATH


@contextmanager
def connect():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database():
    """Cria tabelas ausentes e aplica migrações aditivas, sem apagar dados."""
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS ativos (
            ticker TEXT PRIMARY KEY, nome TEXT, tipo TEXT, ativo INTEGER DEFAULT 1,
            data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT NOT NULL, tipo TEXT NOT NULL,
            quantidade REAL NOT NULL, preco REAL NOT NULL,
            data_operacao TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS carteira (
            ticker TEXT PRIMARY KEY, quantidade REAL NOT NULL, preco_medio REAL NOT NULL,
            data_compra TEXT
        );
        CREATE TABLE IF NOT EXISTS cotacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT NOT NULL, preco REAL NOT NULL,
            minima_dia REAL, maxima_dia REAL, abertura REAL, fechamento_anterior REAL,
            variacao REAL, variacao_percentual REAL, data_hora TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS historico_diario (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT NOT NULL, data_pregao TEXT NOT NULL,
            abertura REAL NOT NULL, maxima REAL NOT NULL, minima REAL NOT NULL,
            fechamento REAL NOT NULL, variacao_percentual REAL NOT NULL, volume REAL,
            UNIQUE(ticker, data_pregao)
        );
        CREATE TABLE IF NOT EXISTS fx_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, base_currency TEXT NOT NULL,
            quote_currency TEXT NOT NULL, rate REAL NOT NULL CHECK(rate > 0),
            observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS gauss_curve (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT NOT NULL,
            retorno REAL NOT NULL, densidade REAL NOT NULL,
            data_calculo TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS analytics_estatistica (
            ticker TEXT PRIMARY KEY, media_retorno REAL, desvio_padrao REAL,
            retorno_atual REAL, z_score REAL, percentil REAL,
            faixa_1_sigma_inf REAL, faixa_1_sigma_sup REAL,
            faixa_2_sigma_inf REAL, faixa_2_sigma_sup REAL,
            faixa_3_sigma_inf REAL, faixa_3_sigma_sup REAL,
            data_calculo TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS histograma_retorno (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT NOT NULL,
            faixa_retorno REAL NOT NULL, frequencia INTEGER NOT NULL,
            percentual_ocorrencia REAL NOT NULL,
            data_calculo TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS portfolio_resumo (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data_referencia TEXT DEFAULT CURRENT_TIMESTAMP,
            total_investido REAL NOT NULL, patrimonio_atual REAL NOT NULL,
            lucro_total REAL NOT NULL, rentabilidade_total REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS portfolio_snapshot (
            ticker TEXT PRIMARY KEY, quantidade REAL NOT NULL, preco_medio REAL NOT NULL,
            preco_atual REAL NOT NULL, valor_investido REAL NOT NULL,
            valor_atual REAL NOT NULL, lucro REAL NOT NULL, rentabilidade REAL NOT NULL,
            ultima_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_quotes_ticker_date ON cotacoes(ticker, data_hora, id);
        CREATE INDEX IF NOT EXISTS idx_mov_ticker_id ON movimentacoes(ticker, id);
        CREATE INDEX IF NOT EXISTS idx_history_ticker_date ON historico_diario(ticker, data_pregao);
        """)

        # Migração 1: metadados de mercado/moeda.
        cols = {row[1] for row in conn.execute("PRAGMA table_info(ativos)")}
        for name in ("mercado", "bolsa", "moeda"):
            if name not in cols:
                conn.execute(f"ALTER TABLE ativos ADD COLUMN {name} TEXT")

        cols = {row[1] for row in conn.execute("PRAGMA table_info(cotacoes)")}
        if "moeda" not in cols:
            conn.execute("ALTER TABLE cotacoes ADD COLUMN moeda TEXT")

        versions = {int(row[0]) for row in conn.execute("SELECT version FROM schema_migrations")}
        if 1 not in versions:
            # Heurística somente para cadastros antigos ainda sem mercado.
            conn.execute("UPDATE ativos SET mercado = CASE WHEN ticker LIKE '%.SA' THEN 'BR' ELSE 'US' END WHERE mercado IS NULL")
            conn.execute("UPDATE ativos SET moeda = CASE WHEN mercado = 'BR' THEN 'BRL' WHEN mercado = 'US' THEN 'USD' END WHERE moeda IS NULL")
            conn.execute("UPDATE ativos SET bolsa = CASE WHEN mercado = 'BR' THEN 'B3' WHEN mercado = 'US' THEN 'NASDAQ/NYSE' END WHERE bolsa IS NULL")
            conn.execute("INSERT INTO schema_migrations(version) VALUES (1)")

        # Preenche apenas moedas ausentes e somente quando há cadastro confiável.
        conn.execute("""
            UPDATE cotacoes
            SET moeda = (SELECT a.moeda FROM ativos a WHERE a.ticker = cotacoes.ticker)
            WHERE moeda IS NULL
              AND EXISTS (SELECT 1 FROM ativos a WHERE a.ticker = cotacoes.ticker AND a.moeda IS NOT NULL)
        """)
