from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = "data/mercado.db"

TOKEN = os.getenv("FINNHUB_TOKEN")

TICKERS = [
    "QQQ",
    "NVDA",
    "MSFT",
    "AAPL",
    "AMZN"
]

COLETA_INTERVALO = 60