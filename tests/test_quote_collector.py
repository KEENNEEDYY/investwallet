from app.collectors import yfinance_collector as collector


def test_yahoo_symbol_mapping():
    assert collector.yahoo_symbol("PETR4", "BR") == "PETR4.SA"
    assert collector.yahoo_symbol("PETR4.SA", "BR") == "PETR4.SA"
    assert collector.yahoo_symbol("AAPL", "US") == "AAPL"


def test_collect_quotes_persists_currency(monkeypatch):
    saved = []
    monkeypatch.setattr(collector, "list_assets", lambda active_only=False: [
        {"ticker": "AAPL", "mercado": "US", "moeda": "USD"}
    ])
    monkeypatch.setattr(collector, "fetch_latest_quote", lambda ticker, market: {
        "ticker": ticker, "preco": 200.0, "minima": 198.0, "maxima": 202.0,
        "abertura": 199.0, "fechamento_anterior": 198.0, "variacao": 2.0,
        "variacao_percentual": 1.01, "moeda": "USD",
        "data_hora": "2026-11-03 12:00:00", "simbolo_fonte": "AAPL",
    })
    monkeypatch.setattr(collector, "insert_quote", lambda **kwargs: saved.append(kwargs))

    results = collector.collect_quotes()
    assert results[0]["status"] == "sucesso"
    assert saved[0]["currency"] == "USD"
    assert saved[0]["price"] == 200.0
