# ---------------------------------------------------------------------------
# Author: Mariana Salgueiro
# ---------------------------------------------------------------------------

import logging
import os

import json

# Inicialização da variável que guarda o logger do módulo
logger = logging.getLogger(__name__)

FILE_CONFIG = os.path.sep.join([os.path.dirname(__file__), 'config.json'])

#Variáveis de ambiente necessárias para que o programa rode
AGRAPH_HOST = os.environ.get('AGRAPH_HOST')
AGRAPH_PORT = int(os.environ.get('AGRAPH_PORT', '10035'))
AGRAPH_USER = os.environ.get('AGRAPH_USER')
AGRAPH_PASSWORD = os.environ.get('AGRAPH_PASSWORD')

def connect():
    """
	Esta função faz a conexão com o banco de dados AllegroGraph

    Parâmetros de entrada:
        nenhum

    Parâmetros de saída:
        conexao: AllegroGraphServer.openFederated
            Conexão com os repositórios em que os dados estão armazenados
	"""
    from franz.openrdf.sail.allegrographserver import AllegroGraphServer
    server = AllegroGraphServer(host=AGRAPH_HOST, port=AGRAPH_PORT, user=AGRAPH_USER, password=AGRAPH_PASSWORD)

    from franz.openrdf.connect import ag_connect
    try:
        conn_pool = []

        #Os nomes dos repositórios em que os dados estão armazenados estão definidos no arquivo json (/app/config.json)
        with open(FILE_CONFIG, 'r') as f:
            j = json.load(f)  # carregando o arquivo de configs
            conns = j['conexoes']   # lista de conexoes
            for conn in conns:
                conn_pool.append(ag_connect(conn))

            conexao = server.openFederated(conn_pool)

            #O arquivo json também contém os namespaces que são necessários para que as consultas sejam executadas
            for key, url in j['repositorios'].items():
                conexao.setNamespace(key, url)  # carrega um namespace

        return conexao
            
    except Exception as e:
        print("Exception : ", e)
        logger.error('Aconteceu alguma excecao na conexao com o banco: %s', e)