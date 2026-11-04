import time
import requests

from app.config import TOKEN

from app.config import COLETA_INTERVALO

from app.database import insert_quote

from app.logger import logger

from app.database import (
    insert_quote,
    get_connection
)



def get_price(symbol):

    url = (
        f"https://finnhub.io/api/v1/quote"
        f"?symbol={symbol}"
        f"&token={TOKEN}"
    )

    response = requests.get(
        url,
        timeout=10
        )

    response.raise_for_status()

    return response.json()


def obter_ativos():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticker
        FROM ativos
        WHERE ativo = 1
    """)

    ativos = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return ativos

def coletar():

    logger.info("Iniciando ciclo de coleta")

    print("\n==========================")
    print("Iniciando coleta...")
    print("==========================")

    for ticker in obter_ativos():

        try:

            dados = get_price(ticker)
            preco = dados["c"]
            minima = dados["l"]
            maxima = dados["h"]
            abertura = dados["o"]
            fechamento_anterior = dados["pc"]
            variacao = dados["d"]
            variacao_percentual = dados["dp"]

            insert_quote(
                ticker=ticker,
                preco=preco,
                minima=minima,
                maxima=maxima,
                abertura=abertura,
                fechamento_anterior=fechamento_anterior,
                variacao=variacao,
                variacao_percentual=variacao_percentual
            )

            message = (
                f"{ticker} | "
                f"Preço: {preco} | "
                f"Mín: {minima} | "
                f"Máx: {maxima} | "
                f"Var%: {variacao_percentual}"
            )

            print(message)
            logger.info(message)

        except Exception as erro:

            message = (
                f"Erro em {ticker}: {erro}"
            )
            print(message)
            logger.error(message)





def main():

    logger.info("Collector iniciado")

    while True:

        try:
            coletar()
            logger.info(
                f"Aguardando {COLETA_INTERVALO} segundos"
            )
            time.sleep(COLETA_INTERVALO)

        except KeyboardInterrupt:

            logger.warning("Colletor encerrado pelo usuário")

            print("\nEncerrado")

            break

        except Exception as erro:

            logger.exception(f"Erro inesperado: {erro}")

            time.sleep(30)


if __name__ == "__main__":
    main()