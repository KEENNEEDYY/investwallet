import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from app.config import FINNHUB_TOKEN


BASE_URL = "https://finnhub.io/api/v1/quote"


class FinnhubRESTCollector:

    def __init__(self):
        if not FINNHUB_TOKEN:
            raise ValueError("FINNHUB_TOKEN não configurado.")

    def get_quote(self, ticker):
        ticker = ticker.strip().upper()

        params = urlencode({"symbol": ticker})
        request = Request(
            f"{BASE_URL}?{params}",
            headers={
                "X-Finnhub-Token": FINNHUB_TOKEN,
                "Accept": "application/json"
            }
        )

        try:
            with urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))

        except HTTPError as error:
            raise RuntimeError(
                f"Erro HTTP Finnhub: {error.code}"
            ) from None

        except URLError:
            raise RuntimeError(
                "Não foi possível conectar à Finnhub."
            ) from None

        current = float(data.get("c") or 0)
        previous = float(data.get("pc") or 0)

        if current <= 0 or previous <= 0:
            raise ValueError(
                f"Finnhub não retornou cotação válida para {ticker}."
            )

        return {
            "ticker": ticker,
            "preco": current,
            "fechamento_anterior": previous,
            "variacao": float(data.get("d") or 0),
            "variacao_percentual": float(data.get("dp") or 0),
            "maxima": float(data.get("h") or 0),
            "minima": float(data.get("l") or 0),
            "abertura": float(data.get("o") or 0),
            "timestamp": int(data.get("t") or 0)
        }