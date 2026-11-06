
import streamlit as st

from app.repositories.portfolio_repository import (
    list_positions,
    list_assets,
)
from app.collectors.finnhub_collector import FinnhubCollector
from app.collectors.finnhub_rest_collector import FinnhubRESTCollector
from app.services.monitoring_service import MonitoringService


def get_all_monitoring_symbols():
    positions = list_positions()
    assets = list_assets(active_only=True)

    position_symbols = {
        position["ticker"].strip().upper()
        for position in positions
        if float(position["quantidade"] or 0) > 0
    }

    asset_symbols = {
        asset["ticker"].strip().upper()
        for asset in assets
        if asset["ticker"]
    }

    return sorted(position_symbols | asset_symbols)


@st.cache_resource
def get_shared_monitoring_service():
    symbols = get_all_monitoring_symbols()

    collector = FinnhubCollector(symbols=symbols)
    rest_collector = FinnhubRESTCollector()

    service = MonitoringService(
        collector,
        rest_collector
    )

    collector.start()

    return collector, service


def refresh_shared_monitoring_symbols(collector):
    symbols = get_all_monitoring_symbols()
    collector.set_symbols(symbols)
    return symbols
