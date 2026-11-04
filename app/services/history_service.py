
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
