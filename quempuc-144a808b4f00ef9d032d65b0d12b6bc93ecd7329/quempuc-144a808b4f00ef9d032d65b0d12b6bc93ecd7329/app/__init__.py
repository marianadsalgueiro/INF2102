# ---------------------------------------------------------------------------
# Author: Mariana Salgueiro
# ---------------------------------------------------------------------------

import os
from flask import Flask, g, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

import logging
from enum import Enum

from config import app_config

from .connection import connect

# db variable initialization
db = SQLAlchemy()


class Namespaces(Enum):
    HOMEPAGE = "<http://xmlns.com/foaf/0.1/homepage>"
    BIOGRAPHY = '<http://purl.org/vocab/bio/0.1/biography>'
    CAD_PUC = '<http://www.nima.puc-rio.br/cad-puc/>'
    MBOX = '<http://xmlns.com/foaf/0.1/mbox>'
    SITUACAO = '<http://www.nima.puc-rio.br/cad-puc/situacao>'
    UNIDADE = '<http://www.nima.puc-rio.br/cad-puc/unidade>'
    TESE = '<http://purl.org/ontology/bibo/Thesis>'
    ARTIGO = '<http://purl.org/ontology/bibo/Article>'
    CAPITULO = '<http://purl.org/ontology/bibo/Chapter>'
    LIVRO = '<http://purl.org/ontology/bibo/Book>'


def get_db():
    """
    Cria conexão com o SQLAlchemy (Python SQL toolkit e Object Relational Mapper).

    Parâmetros de entrada:
       nenhum

    Parâmetros de saída:
        Caso sucesso, g: Flask object.
            Objeto de conexão do SQLAlchemy com o Flask.
        Caso erro, indica status de erro exit(1).
    """

    if 'db' not in g:
        g.db = connect()

    if g.db is None:
        print("######## ERRO CONECTANDO NO ALLEGRO! ##########")
        exit(-1)

    return g.db


def encoded_id(x: str) -> str:
    """
    Recebe uma string e retorna uma string em base64.

    Parâmetros de entrada:
       x: str

    Parâmetros de saída:
        encoded: str em base64
    """

    import base64
    encoded = base64.urlsafe_b64encode(x.encode('utf-8'))
    return encoded.decode('utf-8')


def decoded_id(x: str) -> str:
    """
    Recebe uma string codificada em base64 e retorna a string original.

    Parâmetros de entrada:
       x: str em base64

    Parâmetros de saída:
        decoded: str
    """

    import base64
    decoded = base64.urlsafe_b64decode(x.encode('utf-8'))
    return decoded.decode('utf-8')


def create_app(config_name):
    """
    Cria a aplicação flask com as configurações definidas pelas variáveis de ambiente.

    Parâmetros de entrada:
       config_name: os.getenv('FLASK_CONFIG')

    Parâmetros de saída:
        app: Flask(__name__, instance_relative_config=True)
    """

    # Initialize the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    db.init_app(app)

    logging.basicConfig(filename='quem@puc.log', format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S', level=logging.INFO)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    Bootstrap(app)

    # highlight das palavras
    from .utils import highlight

    # funcoes para preencher html
    from .utils import email_de_problemas, atualizacao_do_lattes, chaves_ordenadas

    app.jinja_env.globals.update(encoded_id=encoded_id, decoded_id=decoded_id, highlight=highlight,
                                 email_de_problemas=email_de_problemas, atualizacao_do_lattes=atualizacao_do_lattes,
                                 enumerate=enumerate,   # o jinja nao tem enumerate
                                 chaves_ordenadas=chaves_ordenadas)
    return app
