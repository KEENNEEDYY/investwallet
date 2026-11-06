
import logging
import statistics
import time
from datetime import date
from statistics import NormalDist

from app.config import FINNHUB_REST_CACHE_SECONDS
from app.services.analytics_service import ticker_analytics

logger = logging.getLogger(__name__)


class MonitoringService:

    def __init__(self, collector, rest_collector=None):
        self.collector = collector
        self.rest_collector = rest_collector
        self._rest_cache = {}
        self._rest_cache_ttl = FINNHUB_REST_CACHE_SECONDS

    @staticmethod
    def classify_alert(z_score):
        value = abs(z_score)

        if value >= 3:
            return "MUITO EXTREMO", "red"
        if value >= 2:
            return "EXTREMO", "orange"
        if value >= 1:
            return "ATENÇÃO", "yellow"

        return "NORMAL", "green"

    def _get_prices(self):
        prices = self.collector.get_prices()
        now = time.monotonic()

        if self.rest_collector is None:
            return prices

        for ticker in self.collector.symbols:
            if ticker in prices:
                continue

            cached = self._rest_cache.get(ticker)

            if cached and now - cached["cached_at"] < self._rest_cache_ttl:
                prices[ticker] = cached["quote"]
                continue

            try:
                quote = self.rest_collector.get_quote(ticker)
                self._rest_cache[ticker] = {
                    "quote": quote,
                    "cached_at": now
                }
                prices[ticker] = quote

            except Exception:
                logger.exception(
                    "Falha ao consultar cotação REST de %s", ticker
                )

                if cached:
                    prices[ticker] = cached["quote"]

        return prices

    def get_monitoring_data(self, period_days=365):
        prices = self._get_prices()
        results = []
        today = date.today().isoformat()

        for ticker, quote in prices.items():
            analytics = ticker_analytics(
                ticker,
                period_days=period_days
            )

            previous_sessions = [
                row for row in analytics["history"]
                if row["data_pregao"] < today
            ]

            if len(previous_sessions) < 2:
                continue

            historical_close = previous_sessions[-1]["fechamento"]

            previous_close = quote.get(
                "fechamento_anterior",
                historical_close
            )

            returns = [
                row["variacao_percentual"]
                for row in previous_sessions
                if row["variacao_percentual"] is not None
            ]

            if len(returns) < 2:
                continue

            mean = statistics.mean(returns)
            stddev = statistics.stdev(returns)

            if stddev <= 0 or previous_close <= 0:
                continue

            current_price = quote["preco"]

            daily_change = (
                current_price / previous_close - 1
            ) * 100

            z_score = (daily_change - mean) / stddev

            percentile = NormalDist(
                mean, stddev
            ).cdf(daily_change) * 100

            alert, color = self.classify_alert(z_score)

            results.append({
                "ticker": ticker,
                "preco": current_price,
                "fechamento_anterior": previous_close,
                "variacao_percentual": daily_change,
                "media_historica": mean,
                "desvio_padrao": stddev,
                "z_score": z_score,
                "percentil": percentile,
                "alerta": alert,
                "cor": color,
                "timestamp": quote.get("timestamp")
            })

        return results
