
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]

_raw_db_path = Path(
    os.getenv("DB_PATH", "data/mercado.db")
).expanduser()

DB_PATH = (
    _raw_db_path
    if _raw_db_path.is_absolute()
    else PROJECT_ROOT / _raw_db_path
)

FINNHUB_TOKEN = os.getenv("FINNHUB_TOKEN", "").strip()

# Configurações de atualização e conexão Finnhub
FINNHUB_WS_RETRY_SECONDS = int(
    os.getenv("FINNHUB_WS_RETRY_SECONDS", "600")
)

FINNHUB_WS_RECONNECT_SECONDS = int(
    os.getenv("FINNHUB_WS_RECONNECT_SECONDS", "60")
)

MONITORING_REFRESH_SECONDS = int(
    os.getenv("MONITORING_REFRESH_SECONDS", "600")
)

FINNHUB_REST_CACHE_SECONDS = int(
    os.getenv("FINNHUB_REST_CACHE_SECONDS", "600")
)

BASE_CURRENCIES = ("BRL", "USD")
