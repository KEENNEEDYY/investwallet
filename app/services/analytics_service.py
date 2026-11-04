import math
import statistics
from datetime import date, timedelta

from app.database.connection import connect


def available_tickers():
    with connect() as conn:
        rows = conn.execute("""
            SELECT ticker
            FROM ativos
            ORDER BY ticker
        """).fetchall()

    return [row["ticker"] for row in rows]


def _normal_cdf(value, mean, stddev):
    """Função de distribuição acumulada da normal."""
    z = (value - mean) / (stddev * math.sqrt(2))
    return (1 + math.erf(z)) / 2


def _build_histogram(returns, mean, stddev):
    if not returns:
        return []

    minimum = min(returns)
    maximum = max(returns)

    bins = max(5, min(20, round(math.sqrt(len(returns)))))

    if minimum == maximum:
        width = max(abs(minimum) * 0.1, 0.1)
        minimum -= width / 2
        maximum += width / 2

    width = (maximum - minimum) / bins
    frequencies = [0] * bins

    for value in returns:
        index = int((value - minimum) / width)
        index = min(index, bins - 1)
        frequencies[index] += 1

    total = len(returns)
    histogram = []

    for index, frequency in enumerate(frequencies):
        lower = minimum + index * width
        upper = lower + width
        center = (lower + upper) / 2

        observed_percent = frequency / total * 100

        # Probabilidade teórica da distribuição normal dentro da faixa.
        if stddev > 0:
            probability = (
                _normal_cdf(upper, mean, stddev)
                - _normal_cdf(lower, mean, stddev)
            )
            gaussian_percent = probability * 100
        else:
            gaussian_percent = 0.0

        histogram.append({
            "faixa": f"{lower:.2f}% a {upper:.2f}%",
            "centro": center,
            "frequencia": frequency,
            "percentual": observed_percent,
            "gauss_percentual": gaussian_percent,
        })

    return histogram


def ticker_analytics(ticker, period_days=None):
    with connect() as conn:
        rows = conn.execute("""
            SELECT data_pregao, fechamento, volume
            FROM historico_diario
            WHERE ticker = ?
            ORDER BY data_pregao
        """, (ticker,)).fetchall()

    raw_history = [dict(row) for row in rows]

    # Calcula o retorno close-to-close antes de aplicar o filtro de período.
    # Assim, o primeiro dia do período pode usar o fechamento do pregão anterior.
    history = []
    previous_close = None

    for row in raw_history:
        close = float(row["fechamento"])

        daily_return = None
        if previous_close is not None and previous_close > 0:
            daily_return = (close / previous_close - 1) * 100

        history.append({
            "data_pregao": row["data_pregao"],
            "fechamento": close,
            "volume": row["volume"],
            "variacao_percentual": daily_return,
        })

        previous_close = close

    if period_days is not None:
        cutoff = (date.today() - timedelta(days=period_days)).isoformat()
        history = [
            row for row in history
            if row["data_pregao"] >= cutoff
        ]

    returns = [
        row["variacao_percentual"]
        for row in history
        if row["variacao_percentual"] is not None
        and math.isfinite(row["variacao_percentual"])
    ]

    result = {
        "ticker": ticker,
        "history": history,
        "samples": len(returns),
        "histogram": [],
        "statistics": None,
    }

    if not returns:
        return result

    mean = statistics.mean(returns)
    stddev = statistics.stdev(returns) if len(returns) > 1 else 0.0
    latest = returns[-1]

    z_score = (
        (latest - mean) / stddev
        if stddev > 0 else 0.0
    )

    percentile = (
        sum(value <= latest for value in returns)
        / len(returns) * 100
    )

    result["statistics"] = {
        "media": mean,
        "desvio_padrao": stddev,
        "retorno_mais_recente": latest,
        "z_score": z_score,
        "percentil": percentile,
        "faixas": {
            "1_sigma": (mean - stddev, mean + stddev),
            "2_sigma": (mean - 2 * stddev, mean + 2 * stddev),
            "3_sigma": (mean - 3 * stddev, mean + 3 * stddev),
        },
    }

    result["histogram"] = _build_histogram(
    returns, mean, stddev
    )

    # Detecção de eventos extremos
    extreme_events = []

    if stddev > 0:
        for row in history:
            daily_return = row["variacao_percentual"]

            if daily_return is None:
                continue

            z_score = (daily_return - mean) / stddev

            if abs(z_score) >= 2:
                extreme_events.append({
                    "data": row["data_pregao"],
                    "retorno": daily_return,
                    "z_score": z_score,
                    "classificacao": (
                        "Extremo - 3 sigmas"
                        if abs(z_score) >= 3
                        else "Extremo - 2 sigmas"
                    ),
                    "direcao": (
                        "Positivo" if daily_return > 0 else "Negativo"
                    ),
                })

    extreme_events.sort(
        key=lambda event: abs(event["z_score"]),
        reverse=True,
    )

    count_2 = sum(
        abs(event["z_score"]) >= 2
        for event in extreme_events
    )

    count_3 = sum(
        abs(event["z_score"]) >= 3
        for event in extreme_events
    )

    total = len(returns)

    result["extremes"] = {
        "eventos": extreme_events,
        "total_2_sigma": count_2,
        "total_3_sigma": count_3,
        "percentual_2_sigma": count_2 / total * 100,
        "percentual_3_sigma": count_3 / total * 100,
        "esperado_2_sigma": math.erfc(2 / math.sqrt(2)) * 100,
        "esperado_3_sigma": math.erfc(3 / math.sqrt(2)) * 100,
        "total_observacoes": total,
    }

    return result