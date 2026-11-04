from app.database import (
    registrar_movimentacao,
    atualizar_carteira,
    listar_carteira,
    listar_movimentacoes
)

from app.portfolio import (
    atualizar_portfolio
)

def menu():

    while True:

        print("\n==========================")
        print("GERENCIAMENTO DE CARTEIRA")
        print("==========================")

        print("1 - Comprar ativo")
        print("2 - Vender ativo")
        print("3 - Ver carteira")
        print("4 - Ver movimentações")
        print("5 - Atualizar carteira")
        print("6 - Sair")

        opcao = input(
            "\nEscolha: "
        )

        if opcao == "1":
            ticker = input(
                "Ticker: "
            ).upper()

            quantidade = float(
                input(
                    "Quantidade: "
                )
            )

            preco = float(
                input(
                    "Preço de compra: "
                )
            )

            registrar_movimentacao(
                ticker=ticker,
                tipo="COMPRA",
                quantidade=quantidade,
                preco=preco
            )

            atualizar_carteira()
            atualizar_portfolio()

            print(
                "\nCompra registrada."
            )

        elif opcao == "2":

            ticker = input(
                "Ticker: "
            ).upper()

            quantidade = float(
                input(
                    "Quantidade: "
                )
            )

            preco = float(
                input(
                    "Preço de venda: "
                )
            )

            registrar_movimentacao(
                ticker=ticker,
                tipo="VENDA",
                quantidade=quantidade,
                preco=preco
            )

            atualizar_carteira()
            atualizar_portfolio()

            print(
                "\nVenda registrada."
            )

        elif opcao == "3":

            print("\nCARTEIRA\n")

            for linha in listar_carteira():

                print(
                    linha
                )

        elif opcao == "4":

            print("\nMOVIMENTAÇÕES\n")

            for linha in listar_movimentacoes():

                print(
                    linha
                )

        elif opcao == "5":

            atualizar_carteira()

            print(
                "\nCarteira atualizada."
            )

        elif opcao == "6":

            print(
                "\nAté logo."
            )

            break


if __name__ == "__main__":

    menu()