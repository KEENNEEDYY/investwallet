
import math
from datetime import date, datetime, timedelta

from app.repositories.portfolio_repository import list_assets
from app.repositories.history_repository import (
    get_latest_history_date,
    save_daily_history,
    insert_missing_daily_history,
)


def collect_asset_history(asset, force_full=False):
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError(
            "yfinance não instalado. Execute: pip install -r requirements.txt"
        ) from exc

    ticker = asset["ticker"].strip().upper()
    market = asset.get("mercado")

    if market not in ("BR", "US"):
        raise ValueError(f"Mercado inválido para {ticker}.")

    symbol = ticker
    if market == "BR" and not ticker.endswith(".SA"):
        symbol = f"{ticker}.SA"

    ultima_data = get_latest_history_date(ticker)

    if force_full:
        history = yf.Ticker(symbol).history(
            period="max",
            interval="1d",
            auto_adjust=False,
            actions=False,
            timeout=30,
        )
        tipo_carga = "reforço_completo"

    elif ultima_data:
        data_inicio = (
            datetime.strptime(ultima_data, "%Y-%m-%d").date()
            - timedelta(days=7)
        )
        history = yf.Ticker(symbol).history(
            start=data_inicio.isoformat(),
            end=(date.today() + timedelta(days=1)).isoformat(),
            interval="1d",
            auto_adjust=False,
            actions=False,
            timeout=30,
        )
        tipo_carga = "incremental"

    else:
        history = yf.Ticker(symbol).history(
            period="max",
            interval="1d",
            auto_adjust=False,
            actions=False,
            timeout=30,
        )
        tipo_carga = "completa"

    if history is None or history.empty:
        raise ValueError(
            f"Yahoo Finance não retornou histórico para {symbol}."
        )

    history = history.dropna(
        subset=["Open", "High", "Low", "Close"]
    ).copy()

    if len(history) < 2:
        raise ValueError(
            f"Histórico insuficiente para calcular retornos de {symbol}."
        )

    history["retorno"] = history["Close"].pct_change() * 100

    records = []

    for data, row in history.iterrows():
        retorno = row["retorno"]

        if retorno is None or not math.isfinite(float(retorno)):
            continue

        values = [
            float(row["Open"]),
            float(row["High"]),
            float(row["Low"]),
            float(row["Close"]),
            float(retorno),
        ]

        if not all(math.isfinite(value) for value in values):
            continue

        volume = row.get("Volume")
        if volume is not None and math.isfinite(float(volume)):
            volume = float(volume)
        else:
            volume = None

        data_pregao = data.strftime("%Y-%m-%d")

        records.append((
            ticker,
            data_pregao,
            values[0],
            values[1],
            values[2],
            values[3],
            values[4],
            volume,
        ))

    if not records:
        raise ValueError(
            f"Nenhum candle válido encontrado para {symbol}."
        )

    if force_full:
        saved = insert_missing_daily_history(records)
    else:
        saved = save_daily_history(records)

    return {
        "ticker": ticker,
        "simbolo": symbol,
        "tipo_carga": tipo_carga,
        "registros": saved,
        "primeira_data": records[0][1],
        "ultima_data": records[-1][1],
    }


def collect_historical_quotes(assets=None):
    assets = assets if assets is not None else list_assets(active_only=True)

    results = []

    for asset in assets:
        ticker = asset["ticker"]

        try:
            result = collect_asset_history(asset)
            results.append({
                **result,
                "status": "sucesso",
            })
        except Exception as exc:
            results.append({
                "ticker": ticker,
                "status": "erro",
                "mensagem": str(exc),
            })

    return results
