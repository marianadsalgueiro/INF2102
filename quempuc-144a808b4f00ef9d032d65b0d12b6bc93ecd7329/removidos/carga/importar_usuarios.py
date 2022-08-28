"""
Script para importar usuarios da base de dados disponibilizada pelo CSV
"""

import psycopg2         # para comunicar com o BD
import csv              # para ler o arquivo
from sys import argv    # para poder chamar o script passando argumentos


def conectar():
    """
    Faz uma conexão com a base de dados, utilizando as variaveis
    do ambiente disponiveis
    :return: conexao com a base de dados
    """

    senha_do_banco = input("Digite a senha do usuario postgres: ")
    porta = input("Digite a porta do postgres: ")
    database_host = input("Digite o nome do banco para inserir os dados: ")

    try:
        return psycopg2.connect(
            f'postgres://postgres:{senha_do_banco}@localhost:{porta}/{database_host}'
        )
    except Exception as e:
        print("Erro ao conectar com o banco: ", e)
        exit(-1)


def ler_arquivo(nome_arquivo: str, sep=';'):
    """
    Abre o arquivo e faz a leitura, convertendo o CSV para uma
    lista de dicionarios
    :param sep: Separador do arquivo CSV. Default é ';'
    :param nome_arquivo: Nome do CSV para ser aberto
    :return: Uma lista de dicionarios, em que cada dicionario é uma linha do CSV
    """
    if not nome_arquivo.endswith('.csv'):
        print("O formato do arquivo não é .csv")
        exit(-2)

    with open(nome_arquivo, 'r', encoding='UTF-8') as f:
        # le cada linha e salva em um dicionario
        lista_final = [x for x in csv.DictReader(f, delimiter=sep)]

    return lista_final


def adiciona_base(lista):
    """
    Adiciona os elementos na tabela.
    :param lista: Lista de dicionario, onde cada dicionario eh um elemento a ser inserido
    :return: None
    """

    tamanho = len(lista)
    x = input("Os %d professores serão INSERIDOS na tabela 'professor'. Deseja prosseguir? [Y/N]: " % tamanho)
    if x.lower() != 'y':
        exit(0)

    # abrindo a conexao
    conexao = conectar()
    cursor = conexao.cursor()

    # exibindo os headers
    headers = list(lista[0].keys())
    print("Colunas no CSV: ")
    for i, h in enumerate(headers):
        print("[%d] %s" % (i + 1, h))

    # pegando as colunas importantes
    t = int(input("Qual dos headers acima diz sobre o tipo do professor (professor/associado/..)? Digite o numero: "))
    nome_tipo = headers[t - 1]
    e = int(input("Qual dos headers acima diz sobre o email do professor? Digite o numero: "))
    nome_email = headers[e - 1]
    n = int(input("Qual dos headers acima diz sobre o nome do professor? Digite o numero: "))
    nome_nome = headers[n - 1]
    s = int(input("Qual dos headers acima diz sobre a situacao do professor? Digite o numero: "))
    nome_situacao = headers[s - 1]
    l = int(input("Qual dos headers acima diz sobre o lattes do professor? Digite o numero: "))
    nome_lattes = headers[l - 1]

    # SQL:
    sql = """INSERT INTO professor (tipo, email, nome, situacao, lattes) VALUES ('%s', '%s', '%s', '%s', '%s')"""

    print("Inserindo dados: ")
    for i, dados in enumerate(lista):
        if i % 50 == 0:
            print("Inseridos %d/%d" % (i, tamanho))

        if dados[nome_tipo] == "Aluno":
            continue

        comando = sql % (dados[nome_tipo], dados[nome_email], dados[nome_nome], dados[nome_situacao], dados[nome_lattes])
        try:
            cursor.execute(comando)
        except Exception as e:
            print("Erro ao inserir linha %d: %s" % (i, str(e)))
            conexao.rollback()

    # commitando
    print("Finalizando")
    conexao.commit()
    cursor.close()
    conexao.close()


if __name__ == "__main__":
    if len(argv) != 2 and len(argv) != 3:
        print("Usage: %s [nome-arquivo.csv] (separador-csv)" % argv[0])
        exit(0)

    filename = argv[1]
    if len(argv) == 3:
        separador = argv[2]
    else:
        separador = ';'

    adiciona_base(ler_arquivo(filename, separador))
