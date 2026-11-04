from app.collectors.historical_collector import collect_historical_quotes


def update_historical_quotes():
    """Atualiza o histórico diário de todos os ativos ativos cadastrados."""
    return collect_historical_quotes()
