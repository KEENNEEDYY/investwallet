from app.repositories.portfolio_repository import (
    list_assets,
    save_asset,
    delete_asset as repository_delete_asset,
)

def get_assets(active_only=False):
    return list_assets(active_only=active_only)


def upsert_asset(ticker, nome, tipo, mercado, bolsa, moeda):
    ticker = (ticker or "").strip().upper()
    nome = (nome or "").strip()
    if not ticker or not nome:
        raise ValueError("Ticker e nome são obrigatórios.")
    if mercado not in ("BR", "US"):
        raise ValueError("Mercado deve ser BR ou US.")
    expected = "BRL" if mercado == "BR" else "USD"
    if moeda != expected:
        raise ValueError(f"Para o mercado {mercado}, a moeda deve ser {expected}.")
    save_asset(ticker, nome, tipo, mercado, bolsa, moeda)


def remove_asset(ticker):
    ticker = (ticker or "").strip().upper()

    if not ticker:
        raise ValueError("Selecione um ativo.")

    return repository_delete_asset(ticker)