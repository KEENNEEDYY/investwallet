from app.services import portfolio_service as service

def test_dashboard_empty_database(monkeypatch):
    monkeypatch.setattr(service, 'list_positions', lambda: [])
    monkeypatch.setattr(service, 'latest_fx', lambda base, quote: None)
    data = service.dashboard_data()
    assert data['positions'] == []
    assert data['combined_brl'] is None

def test_currency_totals_and_conversion(monkeypatch):
    monkeypatch.setattr(service, 'list_positions', lambda: [
        {'ticker':'PETR4.SA','quantidade':2,'preco_medio':10,'preco_atual':12,'moeda':'BRL'},
        {'ticker':'AAPL','quantidade':1,'preco_medio':100,'preco_atual':110,'moeda':'USD'},
    ])
    monkeypatch.setattr(service, 'latest_fx', lambda base, quote: {'rate':5.0,'observed_at':'2026-11-03'})
    data=service.dashboard_data()
    assert data['totals']['BRL']['atual'] == 24
    assert data['totals']['USD']['atual'] == 110
    assert data['combined_brl']['atual_brl'] == 574

def test_migration_preserves_legacy_rows(tmp_path, monkeypatch):
    import sqlite3
    from app.database import connection
    db = tmp_path / 'legacy.db'
    conn = sqlite3.connect(db)
    conn.execute('CREATE TABLE ativos (ticker TEXT PRIMARY KEY, nome TEXT, tipo TEXT, ativo INTEGER DEFAULT 1, data_cadastro TEXT)')
    conn.execute("INSERT INTO ativos(ticker,nome,tipo,ativo) VALUES ('AAPL','Apple','AÇÃO',1)")
    conn.execute('CREATE TABLE cotacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT NOT NULL, preco REAL NOT NULL, data_hora TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute("INSERT INTO cotacoes(ticker,preco) VALUES ('AAPL',200)")
    conn.commit(); conn.close()
    monkeypatch.setattr(connection, 'DB_PATH', db)
    connection.initialize_database()
    conn = sqlite3.connect(db)
    asset = conn.execute('SELECT ticker,mercado,moeda FROM ativos').fetchone()
    quote = conn.execute('SELECT ticker,preco,moeda FROM cotacoes').fetchone()
    conn.close()
    assert asset == ('AAPL','US','USD')
    assert quote == ('AAPL',200.0,'USD')

def test_dashboard_does_not_present_partial_total_as_complete(monkeypatch):
    monkeypatch.setattr(service, 'list_positions', lambda: [
        {'ticker': 'AAPL', 'quantidade': 1, 'preco_medio': 100, 'preco_atual': 110, 'moeda': 'USD'},
        {'ticker': 'MSFT', 'quantidade': 1, 'preco_medio': 200, 'preco_atual': None, 'moeda': 'USD'},
    ])
    monkeypatch.setattr(service, 'latest_fx', lambda base, quote: {'rate': 5.0, 'observed_at': '2026-11-03'})
    data = service.dashboard_data()
    assert data['totals']['USD']['atual'] is None
    assert data['missing_quotes'] == ['MSFT']
    assert data['combined_brl']['atual_brl'] is None
