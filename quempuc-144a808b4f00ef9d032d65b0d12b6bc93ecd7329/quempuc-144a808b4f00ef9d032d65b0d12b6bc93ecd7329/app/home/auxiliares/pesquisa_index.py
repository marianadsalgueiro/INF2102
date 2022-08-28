# ---------------------------------------------------------------------------
# Author: Daniel Guimarães
# ---------------------------------------------------------------------------

from ...termos import t as lista_termos
from ...models import Carregamento
from ... import get_db, create_app
from .functions import getNomes, searchInRepository
from . import atualiza_status

from difflib import get_close_matches
from os import path, getenv
from json import dump


def pesquisa_index(busca: str, codigo: int):
    """
    Faz as queries para a pagina do index
    :param busca: string buscada pelo usuario
    :param codigo: codigo para salvar as atualizacoes no banco de dados
        e tambem o resultado
    :return: Dicionario no formato:
        "nomes": lista de nomes para ser exibida na pagina
        "dados": os outros resultados da pesquisa para serem exibidos
        "matching": palavras parecidas
    Caso algum erro ocorrer, será retornado uma string com o erro
    """

    # iniciando o contexto para poder executar o sqlalchemy estando
    # fora do app (numa thread)
    ctx = create_app(getenv('FLASK_CONFIG')).app_context()
    ctx.push()
    carregamento = Carregamento.query.filter_by(id=codigo).first()

    d = dict()
    atualiza_status(carregamento, "Consulta %s iniciada" % busca, percent=5)

    # examinando resultados parecidos
    # por enquanto, retorna uma string vazia pois o termos está vazio

    matches = get_close_matches(busca, lista_termos, cutoff=0.6)
    if busca in matches:
        matches.remove(busca)
    d['matching'] = matches
    atualiza_status(carregamento, "Verificado palavras semelhantes", percent=20)

    # pesquisando os nomes
    d['nomes'] = getNomes(get_db(), pesquisa=busca)
    atualiza_status(carregamento, "Nomes coletados", percent=50)

    # pesquisando os dados
    d['dados'] = searchInRepository(get_db(), string_buscada=busca, atualizar_status=carregamento)
    atualiza_status(carregamento, "Dados gerais coletados", percent=100)

    # salvando o resultado em um arquivo json
    filename = path.join(path.dirname(__file__), '..', 'pesquisas', f'{codigo}.json')
    print("Salvando o arquivo")
    with open(filename, 'w+') as f:
        dump(d, f, indent=3)

    return d
