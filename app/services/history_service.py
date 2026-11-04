
from app.collectors.historical_collector import (
    collect_asset_history,
    collect_historical_quotes,
)


def update_historical_quotes():
    """Atualiza o histórico diário de todos os ativos ativos cadastrados."""
    return collect_historical_quotes()


def update_asset_history(ticker, mercado):
    """Carrega ou atualiza o histórico de um ativo específico."""
    asset = {
        "ticker": ticker,
        "mercado": mercado,
    }
    return collect_asset_history(asset)


def reinforce_insufficient_histories():
    """
    Reforça os históricos classificados como Básico,
    Insuficiente ou Sem histórico.
    """
    from app.services.history_quality_service import (
        evaluate_history_quality,
    )
    from app.repositories.portfolio_repository import list_assets

    quality = evaluate_history_quality()

    target_status = {
        "Em formação",
        "Insuficiente",
        "Sem histórico",
    }

    target_tickers = {
        item["ticker"]
        for item in quality
        if item["status"] in target_status
    }

    assets = list_assets(active_only=True)

    selected_assets = [
        asset
        for asset in assets
        if asset["ticker"] in target_tickers
    ]

    results = []

    for asset in selected_assets:
        ticker = asset["ticker"]

        try:
            result = collect_asset_history(
                asset,
                force_full=True,
            )
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