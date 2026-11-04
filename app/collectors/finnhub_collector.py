import json
import logging
import threading
import time

import websocket

from app.config import FINNHUB_TOKEN

logger = logging.getLogger(__name__)

DEFAULT_SYMBOLS = ("AAPL", "SOXX")


class FinnhubCollector:

    def __init__(self, symbols=None):
        if not FINNHUB_TOKEN:
            raise ValueError("FINNHUB_TOKEN não configurado no .env")

        initial_symbols = DEFAULT_SYMBOLS if symbols is None else symbols

        self.symbols = tuple(sorted({
            str(symbol).strip().upper()
            for symbol in initial_symbols
            if symbol
        }))

        self._lock = threading.Lock()
        self._send_lock = threading.Lock()
        self._prices = {}
        self._connected = False
        self._running = False
        self._ws = None
        self._thread = None

    def set_symbols(self, symbols):
        new_symbols = tuple(sorted({
            str(symbol).strip().upper()
            for symbol in symbols
            if symbol
        }))

        with self._lock:
            old_symbols = set(self.symbols)
            new_set = set(new_symbols)

            added = new_set - old_symbols
            removed = old_symbols - new_set

            self.symbols = new_symbols

            for symbol in removed:
                self._prices.pop(symbol, None)

            ws = self._ws if self._connected else None

        if ws:
            with self._send_lock:
                for symbol in removed:
                    ws.send(json.dumps({
                        "type": "unsubscribe",
                        "symbol": symbol
                    }))

                for symbol in added:
                    ws.send(json.dumps({
                        "type": "subscribe",
                        "symbol": symbol
                    }))

        logger.info(
            "Ativos atualizados. Adicionados: %s | Removidos: %s",
            added,
            removed
        )

    def _on_open(self, ws):
        with self._lock:
            self._connected = True
            symbols = self.symbols

        logger.info("Conectado à Finnhub.")

        with self._send_lock:
            for symbol in symbols:
                ws.send(json.dumps({
                    "type": "subscribe",
                    "symbol": symbol
                }))
                logger.info("Inscrito em %s", symbol)

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)

            if data.get("type") != "trade":
                return

            trades = data.get("data", [])

            with self._lock:
                for trade in trades:
                    symbol = trade.get("s")
                    price = trade.get("p")

                    if symbol not in self.symbols or price is None:
                        continue

                    self._prices[symbol] = {
                        "ticker": symbol,
                        "preco": float(price),
                        "timestamp": trade.get("t"),
                        "recebido_em": time.time()
                    }

        except (ValueError, TypeError, KeyError):
            logger.exception("Erro ao processar mensagem Finnhub.")

    def _on_error(self, ws, error):
        logger.error("Erro Finnhub: %s", error)

    def _on_close(self, ws, status_code, message):
        with self._lock:
            self._connected = False

        logger.warning(
            "Conexão Finnhub encerrada: %s - %s",
            status_code,
            message
        )

    def _run(self):
        while self._running:
            try:
                self._ws = websocket.WebSocketApp(
                    f"wss://ws.finnhub.io?token={FINNHUB_TOKEN}",
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )

                self._ws.run_forever(
                    ping_interval=30,
                    ping_timeout=10
                )

            except Exception:
                logger.exception("Falha na conexão Finnhub.")

            finally:
                with self._lock:
                    self._connected = False

            if self._running:
                time.sleep(5)

    def start(self):
        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="FinnhubCollector"
        )

        self._thread.start()

    def stop(self):
        self._running = False

        if self._ws:
            self._ws.close()

    def get_prices(self):
        with self._lock:
            return {
                symbol: data.copy()
                for symbol, data in self._prices.items()
            }

    def is_connected(self):
        with self._lock:
            return self._connected
