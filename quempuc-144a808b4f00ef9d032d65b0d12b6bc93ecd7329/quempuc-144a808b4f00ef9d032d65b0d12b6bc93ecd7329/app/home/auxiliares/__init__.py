# ---------------------------------------------------------------------------
# Author: Daniel Guimarães
# ---------------------------------------------------------------------------

from ... import db
from ...models import Carregamento


def atualiza_status(objeto: Carregamento, status: str, percent: int):
    """
    Atualiza o objeto Carregamento com o status e porcentagem fornecida
    :param objeto: objeto Carregamento para atualizar
    :param status: string com o status do carregamento
    :param percent: inteiro entre 0 a 100 contendo quanto ja foi feito da pesquisa
    """

    objeto.status = status
    objeto.percent = percent
    db.session.add(objeto)
    db.session.commit()
