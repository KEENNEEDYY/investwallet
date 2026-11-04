
import math

from app.database.connection import connect
from datetime import date, datetime, timedelta


def evaluate_history_quality():
    """
    Avalia a qualidade dos históricos dos ativos cadastrados.
    Operação somente de leitura: não modifica o banco.
    """

    with connect() as conn:
        assets = conn.execute("""
            SELECT ticker, nome, mercado, moeda, ativo
            FROM ativos
            ORDER BY ticker
        """).fetchall()

        results = []

        for asset in assets:
            ticker = asset["ticker"]

            stats = conn.execute("""
                SELECT
                    COUNT(*) AS total_registros,
                    MIN(data_pregao) AS primeira_data,
                    MAX(data_pregao) AS ultima_data,
                    SUM(
                    CASE
                        WHEN abertura <= 0
                        OR maxima <= 0
                        OR minima <= 0
                        OR fechamento <= 0
                        OR maxima < minima * 0.999
                        OR maxima < abertura * 0.999
                        OR maxima < fechamento * 0.999
                        OR minima > abertura * 1.001
                        OR minima > fechamento * 1.001
                        OR ABS(variacao_percentual) > 1000
                        THEN 1
                        ELSE 0
                    END
                ) AS registros_invalidos
                FROM historico_diario
                WHERE ticker = ?
            """, (ticker,)).fetchone()

            total = stats["total_registros"] or 0
            invalidos = stats["registros_invalidos"] or 0

            if total == 0:
                status = "Sem histórico"

            elif invalidos > 0:
                status = "Com problemas"

            elif total >= 120:
                status = "Adequado"

            else:
                primeira_data = stats["primeira_data"]
                data_inicio = datetime.strptime(
                    primeira_data, "%Y-%m-%d"
                ).date()

                limite_recente = date.today() - timedelta(days=365)

                if data_inicio >= limite_recente:
                    status = "Em formação"
                else:
                    status = "Insuficiente"

            percentual_invalido = (
                invalidos / total * 100 if total else 0
            )

            results.append({
                "ticker": ticker,
                "nome": asset["nome"],
                "mercado": asset["mercado"],
                "ativo": bool(asset["ativo"]),
                "total_registros": total,
                "primeira_data": stats["primeira_data"],
                "ultima_data": stats["ultima_data"],
                "registros_invalidos": invalidos,
                "percentual_invalido": round(
                    percentual_invalido, 2
                ),
                "status": status,
            })

    return results
