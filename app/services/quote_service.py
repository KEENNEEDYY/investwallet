from app.collectors.yfinance_collector import collect_quotes


def update_quotes():
    return collect_quotes()
