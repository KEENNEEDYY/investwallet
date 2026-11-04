import sqlite3
import pytest

from app.database import connection
from app.services.movement_service import register_movement


def setup_db(path):
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE ativos(ticker TEXT PRIMARY KEY, ativo INTEGER DEFAULT 1);
        CREATE TABLE movimentacoes(
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT, tipo TEXT,
            quantidade REAL, preco REAL, data_operacao TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE carteira(
            ticker TEXT PRIMARY KEY, quantidade REAL NOT NULL,
            preco_medio REAL NOT NULL, data_compra TEXT
        );
        INSERT INTO ativos(ticker,ativo) VALUES ('AAPL',1);
    """)
    conn.commit()
    conn.close()


def test_weighted_average_and_partial_sale(tmp_path, monkeypatch):
    db = tmp_path / "movements.db"
    setup_db(db)
    monkeypatch.setattr(connection, "DB_PATH", db)

    register_movement("AAPL", "COMPRA", 10, 10)
    register_movement("AAPL", "COMPRA", 10, 20)
    register_movement("AAPL", "VENDA", 5, 30)

    conn = sqlite3.connect(db)
    position = conn.execute("SELECT quantidade, preco_medio FROM carteira WHERE ticker='AAPL'").fetchone()
    movement_count = conn.execute("SELECT COUNT(*) FROM movimentacoes").fetchone()[0]
    conn.close()

    assert position[0] == pytest.approx(15)
    assert position[1] == pytest.approx(15)
    assert movement_count == 3


def test_rejects_sale_above_available_quantity(tmp_path, monkeypatch):
    db = tmp_path / "movements.db"
    setup_db(db)
    monkeypatch.setattr(connection, "DB_PATH", db)
    register_movement("AAPL", "COMPRA", 2, 100)

    with pytest.raises(ValueError, match="Quantidade insuficiente"):
        register_movement("AAPL", "VENDA", 3, 110)

    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM movimentacoes").fetchone()[0]
    conn.close()
    assert count == 1
