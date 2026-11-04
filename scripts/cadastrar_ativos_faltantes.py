from pathlib import Path
import sys
import sqlite3

# Permite executar o script diretamente a partir da pasta scripts/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import DB_PATH


# Cadastro dos 17 ativos que estavam faltando.
# Todos foram classificados como mercado americano e moeda USD.
ATIVOS = [
    ("AAPL", "Apple Inc.", "AÇÃO"),
    ("AVGO", "Broadcom Inc.", "AÇÃO"),
    ("BAC", "Bank of America Corporation", "AÇÃO"),
    ("BND", "Vanguard Total Bond Market ETF", "ETF"),
    ("BNDW", "Vanguard Total World Bond ETF", "ETF"),
    ("CAT", "Caterpillar Inc.", "AÇÃO"),
    ("CVX", "Chevron Corporation", "AÇÃO"),
    ("FDX", "FedEx Corporation", "AÇÃO"),
    ("GOOGL", "Alphabet Inc. Class A", "AÇÃO"),
    ("KO", "The Coca-Cola Company", "AÇÃO"),
    ("LLY", "Eli Lilly and Company", "AÇÃO"),
    ("ORCL", "Oracle Corporation", "AÇÃO"),
    ("SNDK", "Sandisk Corporation", "AÇÃO"),
    ("STAG", "STAG Industrial Inc.", "REIT"),
    ("STX", "Seagate Technology Holdings plc", "AÇÃO"),
    ("TTWO", "Take-Two Interactive Software Inc.", "AÇÃO"),
    ("XOM", "Exxon Mobil Corporation", "AÇÃO"),
]


def main():
    print(f"Banco utilizado: {DB_PATH}")

    if not Path(DB_PATH).exists():
        raise FileNotFoundError(f"Banco de dados não encontrado: {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("BEGIN IMMEDIATE")

        inseridos = 0

        for ticker, nome, tipo in ATIVOS:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO ativos
                    (ticker, nome, tipo, ativo, mercado, bolsa, moeda)
                VALUES (?, ?, ?, 1, 'US', 'NASDAQ/NYSE', 'USD')
                """,
                (ticker, nome, tipo),
            )

            if cursor.rowcount == 1:
                print(f"[CADASTRADO] {ticker} - {nome}")
                inseridos += 1
            else:
                print(f"[JÁ EXISTIA] {ticker}")

        # Preenche a moeda das cotações antigas que ainda estão sem moeda,
        # usando o cadastro correspondente do ativo.
        cursor = conn.execute(
            """
            UPDATE cotacoes
            SET moeda = (
                SELECT ativos.moeda
                FROM ativos
                WHERE ativos.ticker = cotacoes.ticker
            )
            WHERE moeda IS NULL
              AND EXISTS (
                SELECT 1
                FROM ativos
                WHERE ativos.ticker = cotacoes.ticker
                  AND ativos.moeda IS NOT NULL
              )
            """
        )

        cotacoes_atualizadas = cursor.rowcount

        conn.commit()

        print("\n===================================")
        print(f"Novos ativos cadastrados: {inseridos}")
        print(f"Cotações com moeda preenchida: {cotacoes_atualizadas}")
        print("Operação concluída com sucesso.")
        print("Movimentações e posições da carteira foram preservadas.")
        print("===================================")

    except Exception:
        conn.rollback()
        print("\nERRO: operação cancelada. Nenhuma alteração foi confirmada.")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()