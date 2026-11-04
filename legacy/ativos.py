from app.database import (
    inserir_ativo,
    listar_ativos,
    excluir_ativo
)


def menu():

    while True:

        print("\n====================")
        print("ATIVOS")
        print("====================")

        print("1 - Listar")
        print("2 - Adicionar")
        print("3 - Desativar")
        print("4 - Sair")

        opcao = input(
            "\nEscolha: "
        )

        if opcao == "1":

            ativos = listar_ativos()

            for ativo in ativos:

                print(ativo)

        elif opcao == "2":

            ticker = input(
                "Ticker: "
            )

            nome = input(
                "Nome: "
            )

            tipo = input(
                "Tipo (ACAO/ETF): "
            )

            inserir_ativo(
                ticker,
                nome,
                tipo
            )

            print(
                "Ativo adicionado."
            )

        elif opcao == "3":

            ticker = input(
                "Ticker: "
            )

            excluir_ativo(
                ticker
            )

            print(
                "Ativo desativado."
            )

        elif opcao == "4":

            break


if __name__ == "__main__":
    menu()