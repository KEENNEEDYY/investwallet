import statistics
import math

from collections import Counter

from app.database import get_connection

from app.database import (
    obter_ativos
)

from app.database import (
    get_connection,
    salvar_estatistica
)
from app.database import (
    salvar_ponto_gauss
)


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

def gaussian(x, media, desvio):

    return (

        1

        /

        (
            desvio
            *
            math.sqrt(
                2 * math.pi
            )
        )

    ) * math.exp(

        -(

            (
                x - media
            ) ** 2

        )

        /

        (

            2
            *
            desvio**2

        )

    )

def gerar_curva_gauss(ticker):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            media_retorno,
            desvio_padrao

        FROM analytics_estatistica

        WHERE ticker = ?
    """, (ticker,))

    resultado = cursor.fetchone()

    conn.close()

    media = resultado[0]

    desvio = resultado[1]

    limite_inferior = (
        media
        - (4 * desvio)
    )

    limite_superior = (
        media
        + (4 * desvio)
    )

    pontos = 200

    incremento = (
        limite_superior
        - limite_inferior
    ) / pontos

    x = limite_inferior

    while x <= limite_superior:

        densidade = gaussian(
            x,
            media,
            desvio
        )

        salvar_ponto_gauss(
            ticker=ticker,
            retorno=round(x, 4),
            densidade=densidade
        )

        x += incremento

    print(
        f"Curva Gauss criada: {ticker}"
    )

def gerar_estatisticas(ticker):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT variacao_percentual

        FROM historico_diario

        WHERE ticker = ?

        ORDER BY data_pregao
    """, (ticker,))

    retornos = [
        linha[0]
        for linha in cursor.fetchall()
    ]

    conn.close()

    media = statistics.mean(retornos)

    desvio = statistics.stdev(retornos)

    retorno_atual = retornos[-1]

    if desvio == 0:
        z_score = 0

    else:
        z_score = (
            retorno_atual - media
        ) / desvio

    menores = len([
        x for x in retornos
        if x <= retorno_atual
    ])

    percentil = (
        menores
        / len(retornos)
    ) * 100

    salvar_estatistica(

        ticker=ticker,

        media_retorno=round(media, 4),

        desvio_padrao=round(desvio, 4),

        retorno_atual=round(retorno_atual, 4),

        z_score=round(z_score, 4),

        percentil=round(percentil, 2),

        faixa_1_sigma_inf=round(
            media - desvio,
            4
        ),

        faixa_1_sigma_sup=round(
            media + desvio,
            4
        ),

        faixa_2_sigma_inf=round(
            media - (2 * desvio),
            4
        ),

        faixa_2_sigma_sup=round(
            media + (2 * desvio),
            4
        ),

        faixa_3_sigma_inf=round(
            media - (3 * desvio),
            4
        ),

        faixa_3_sigma_sup=round(
            media + (3 * desvio),
            4
        )
    )

    print(
        f"{ticker} processado"
    )

def limpar_histograma():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM histograma_retorno
    """)

    conn.commit()

    conn.close()

def gerar_histograma_ticker(ticker):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT variacao_percentual
        FROM historico_diario
        WHERE ticker = ?
    """, (ticker,))

    retornos = [
        linha[0]
        for linha in cursor.fetchall()
    ]

    conn.close()

    classes = []

    for retorno in retornos:

        faixa = round(retorno)

        classes.append(faixa)

    frequencias = Counter(classes)

    total_amostras = len(retornos)

    conn = get_connection()

    cursor = conn.cursor()

    for faixa in range(-15, 16):

        frequencia = frequencias.get(
            faixa,
            0
        )

        percentual = round(
            (
                frequencia
                / total_amostras
            )
            * 100,
            2
        )

        cursor.execute("""
            INSERT INTO histograma_retorno(
                ticker,
                faixa_retorno,
                frequencia,
                percentual_ocorrencia
            )
            VALUES(
                ?, ?, ?, ?
            )
        """, (
            ticker,
            faixa,
            frequencia,
            percentual
        ))

    conn.commit()

    conn.close()

    print(
        f"{ticker} processado."
    )


def main():

    limpar_histograma()

    for ticker in obter_ativos():

        gerar_histograma_ticker(
            ticker
        )

        gerar_estatisticas(
            ticker
        )

        gerar_curva_gauss(
            ticker
        )

    print(
        "\nAnalytics completo gerado."
    )

if __name__ == "__main__":
    main()