# ---------------------------------------------------------------------------
# Author: Mariana Salgueiro e Daniel Guimarães
# ---------------------------------------------------------------------------

from flask import request

from . import db
from .models import Busca, Frequencia_Termos

import datetime
import os
import json

FILE_CONFIG = os.path.sep.join([os.path.dirname(__file__), 'config.json'])


def email_de_problemas():
    """
	Esta função pega o email do arquivo de configuracao

    Parâmetros de entrada:
        nenhum

    Parâmetros de saída:
        email: str
    """
    with open(FILE_CONFIG, 'r') as f:
        email = json.load(f)['email']
    return email


def atualizacao_do_lattes():
    """
	Esta função pega a última data de atualização dos lattes

    Parâmetros de entrada:
        nenhum

    Parâmetros de saída:
        lattes: str
    """
    with open(FILE_CONFIG, 'r') as f:
        lattes = json.load(f)['lattes']
    return lattes


def highlight(string, termo):
    """
    Acha na string o termo pesquisado, e retorna uma copia da string com o termo colorido atraves de html.
    Caso nao contenha o termo, ele retorna a string original.

    OBS: O termo colorido sera colocado em letras maiusculas, com fundo amarelo, em ASCII.

    Parâmetros de entrada:
        string: str
            Texto original recuperado.
        termo: str
            Termo de busca.

    Parâmetros de saída:
        string: str
            Texto com o termo colorido.
    """

    import unidecode  # para converter tudo para ASCII, para o regex achar melhor
    import re
    from markupsafe import Markup

    # tirando caracteres non-ASCII do termo e da string
    termo_convertido = unidecode.unidecode(termo)
    string_convertida = unidecode.unidecode(string)

    # html para deixar o termo colorido
    colorido = '<span style="background-color:yellow">%s</span>'

    # criando a expressao regular
    expressao = termo_convertido
    expressao = expressao.replace('*', '[a-zA-Z]*')  # troca o asterisco para dar match em qualquer letra n vezes
    expressao = expressao.replace('?', '[a-zA-Z]')  # troca a interrogacao para dar match em qualquer letra 1 vez
    p = re.compile(expressao, re.IGNORECASE)  # ignora se eh maiusculo ou minusculo

    iterador = p.finditer(string_convertida)  # ao iterar, retorna um match
    quantidade_de_matchs = 0

    alteracao_posicao = 0

    for match in iterador:
        inicio, fim = match.span()  # pega a posicao do inicio e do fim do match na string

        inicio += alteracao_posicao
        fim += alteracao_posicao

        # pega o match, colore, e insere no meio da string original non-ASCII
        string = string[:inicio] + colorido % match.group().upper() + string[fim:]

        alteracao_posicao += len(colorido % match.group().upper()) - (fim - inicio)

    if quantidade_de_matchs > 0:
        return Markup(string)  # aqui, a string vai ter sido modificada inserindo a parte colorida
    return string  # caso nao haja nenhum match


def registro_busca(string):
    """
    Registra o termo buscado na pesquisa para geração de nuvem de palavras e mostrar em dashboard palavras buscadas.

    Parâmetros de entrada:
        string: str
            Termo de busca.

    Parâmetros de saída:
        Caso sucesso, nenhum.
        Caso erro, print da exceção.
    """

    if request.headers.getlist('X-Forwarded-For'):
        ip = request.headers.getlist('X-Forwarded-For')[0]
    else:
        ip = request.remote_addr

    busca = Busca(data_e_hora=datetime.datetime.now(), ip=ip, sistema_operacional=request.user_agent.platform, browser=request.user_agent.browser, palavra_buscada=string)

    try:
        db.session.add(busca)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        

def registro_frequencia(string):
    """
    Registra a frequência do termo buscado para geração de nuvem de palavras e mostrar em dashboard palavras frequentes.

    Parâmetros de entrada:
        string: str
            Termo de busca.

    Parâmetros de saída:
        Caso sucesso, nenhum.
        Caso erro, print da exceção.
    """
    termo = Frequencia_Termos.query.filter_by(pk_palavra=string.lower()).first()

    if termo is None:
        frequencia = Frequencia_Termos(pk_palavra=string, count=1)
        db.session.add(frequencia)
    else:
        termo.count += 1

    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()


def chaves_ordenadas(dicionario: dict) -> iter:
    """
    Recebe um dicionario e retorna um iterador sobre as chaves em ordem alfabetica decrescente.
    
    Parâmetros de entrada:
        dicionario: dict

    Parâmetros de saída:
        iter: iter
    """
    return iter(sorted(list(dicionario.keys()), reverse=True))
