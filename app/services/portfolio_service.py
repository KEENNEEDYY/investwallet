from app.repositories.portfolio_repository import list_positions, latest_fx


def dashboard_data():
    positions = list_positions()
    fx = latest_fx("USD", "BRL")
    usd_brl = float(fx["rate"]) if fx else None
    currencies = ("BRL", "USD")
    totals = {
        currency: {
            "investido": 0.0, "atual": None, "posicoes": 0,
            "cotacoes_ok": 0, "cotacoes_faltantes": [],
        }
        for currency in currencies
    }
    enriched = []
    unknown_currency = []

    for original in positions:
        p = dict(original)
        qty = float(p["quantidade"])
        avg = float(p["preco_medio"])
        currency = p.get("moeda")
        price = p.get("preco_atual")
        invested = qty * avg
        current = qty * float(price) if price is not None else None

        if currency not in totals:
            unknown_currency.append(p["ticker"])
        else:
            bucket = totals[currency]
            bucket["posicoes"] += 1
            bucket["investido"] += invested
            if current is None:
                bucket["cotacoes_faltantes"].append(p["ticker"])
            else:
                bucket["cotacoes_ok"] += 1

        p.update(
            valor_investido=invested,
            valor_atual=current,
            lucro=(current - invested) if current is not None else None,
            rentabilidade=((current / invested) - 1) * 100
            if current is not None and invested > 0 else None,
        )
        enriched.append(p)

    for currency, bucket in totals.items():
        if bucket["posicoes"] > 0 and not bucket["cotacoes_faltantes"]:
            bucket["atual"] = sum(
                float(p["valor_atual"])
                for p in enriched
                if p.get("moeda") == currency
            )

    all_quotes_complete = bool(positions) and all(p["preco_atual"] is not None for p in positions)
    all_currencies_known = not unknown_currency and all(p.get("moeda") in currencies for p in positions)
    combined = None
    if usd_brl is not None and all_currencies_known:
        invested_brl = totals["BRL"]["investido"] + totals["USD"]["investido"] * usd_brl
        current_brl = None
        if all_quotes_complete:
            current_brl = (totals["BRL"]["atual"] or 0.0) + (totals["USD"]["atual"] or 0.0) * usd_brl
        combined = {
            "investido_brl": invested_brl,
            "atual_brl": current_brl,
            "lucro_brl": current_brl - invested_brl if current_brl is not None else None,
            "completo": all_quotes_complete,
        }

    return {
        "positions": enriched,
        "totals": totals,
        "usd_brl": usd_brl,
        "combined_brl": combined,
        "fx_timestamp": fx["observed_at"] if fx else None,
        "all_quotes_complete": all_quotes_complete,
        "missing_quotes": [p["ticker"] for p in enriched if p["preco_atual"] is None],
        "unknown_currency": unknown_currency,
    }
