from datetime import datetime, timezone
import math

from app.repositories.portfolio_repository import list_assets, insert_quote


def yahoo_symbol(ticker, market):
    ticker = ticker.strip().upper()
    if market == "BR" and not ticker.endswith(".SA"):
        return f"{ticker}.SA"
    return ticker


def _number(row, column):
    value = row.get(column) if hasattr(row, "get") else row[column]
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def fetch_latest_quote(ticker, market):
    """Busca o último candle diário disponível no Yahoo Finance."""
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError(
            "A biblioteca yfinance não está instalada. Execute: pip install -r requirements.txt"
        ) from exc

    symbol = yahoo_symbol(ticker, market)
    history = yf.Ticker(symbol).history(
        period="5d", interval="1d", auto_adjust=False, actions=False, timeout=20
    )
    if history is None or history.empty:
        raise ValueError(f"Nenhuma cotação retornada para {symbol}.")

    history = history.dropna(subset=["Close"])
    if history.empty:
        raise ValueError(f"Cotação sem preço de fechamento para {symbol}.")

    row = history.iloc[-1]
    close = _number(row, "Close")
    if close is None or close <= 0:
        raise ValueError(f"Preço de fechamento inválido para {symbol}.")

    previous_close = None
    if len(history) > 1:
        previous_close = _number(history.iloc[-2], "Close")
    change = close - previous_close if previous_close is not None else None
    change_percent = (change / previous_close * 100) if previous_close else None

    return {
        "ticker": ticker.upper(),
        "preco": close,
        "minima": _number(row, "Low"),
        "maxima": _number(row, "High"),
        "abertura": _number(row, "Open"),
        "fechamento_anterior": previous_close,
        "variacao": change,
        "variacao_percentual": change_percent,
        "moeda": "BRL" if market == "BR" else "USD",
        # Timestamp de coleta para manter ordenação consistente do histórico de cotações.
        "data_hora": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "simbolo_fonte": symbol,
    }


def collect_quotes(assets=None):
    assets = assets if assets is not None else list_assets(active_only=True)
    results = []
    for asset in assets:
        ticker = asset["ticker"]
        market = asset.get("mercado")
        currency = asset.get("moeda")
        if market not in ("BR", "US") or currency not in ("BRL", "USD"):
            results.append({"ticker": ticker, "status": "erro", "mensagem": "Mercado/moeda não configurados."})
            continue
        try:
            quote = fetch_latest_quote(ticker, market)
            if quote["moeda"] != currency:
                raise ValueError(f"Moeda da cotação ({quote['moeda']}) diverge do cadastro ({currency}).")
            insert_quote(
                ticker=quote["ticker"], price=quote["preco"], currency=quote["moeda"],
                low=quote["minima"], high=quote["maxima"], open_price=quote["abertura"],
                previous_close=quote["fechamento_anterior"], change=quote["variacao"],
                change_percent=quote["variacao_percentual"], observed_at=quote["data_hora"],
            )
            results.append({
                "ticker": ticker, "status": "sucesso", "preco": quote["preco"],
                "moeda": quote["moeda"], "fonte": quote["simbolo_fonte"],
            })
        except Exception as exc:
            results.append({"ticker": ticker, "status": "erro", "mensagem": str(exc)})
    return results
