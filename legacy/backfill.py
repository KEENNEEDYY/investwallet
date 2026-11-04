from datetime import datetime

import yfinance as yf

from app.database import insert_historico

from app.database import (
    obter_ativos
)

def processar_ticker(ticker):

    print(f"\nProcessando {ticker}")

    ativo = yf.Ticker(ticker)

    df = ativo.history(
        period="1y",
        interval="1d",
        auto_adjust=False
    )

    if df.empty:

        print(
            f"Nenhum dado encontrado para {ticker}"
        )

        return

    print(
        f"{len(df)} pregões encontrados"
    )

    for data, row in df.iterrows():

        abertura = float(row["Open"])
        maxima = float(row["High"])
        minima = float(row["Low"])
        fechamento = float(row["Close"])
        volume = float(row["Volume"])


        if abertura == 0:
            continue

        variacao_percentual = round(
            (
            (fechamento - abertura) / abertura
            ) * 100, 
            2
        )





        data_pregao = data.strftime(
            "%Y-%m-%d"
        )

        insert_historico(
            ticker=ticker,
            data_pregao=data_pregao,
            abertura=abertura,
            maxima=maxima,
            minima=minima,
            fechamento=fechamento,
            variacao_percentual=variacao_percentual,
            volume=volume
        )

    print(
        f"{ticker} carregado com sucesso"
    )



def main():

    print(
        "\nINICIANDO BACKFILL HISTÓRICO\n"
    )

    for ticker in obter_ativos(): 
        try:
            processar_ticker(ticker)

        except Exception as erro:
            print(
                f"Erro em {ticker}: {erro}"
            )
        print(
            "\nBACKFILL FINALIZADO\n"
        )

if __name__ == "__main__":
    main()