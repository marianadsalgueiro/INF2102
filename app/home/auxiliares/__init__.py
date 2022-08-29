# ---------------------------------------------------------------------------
# Author: Daniel Guimarães
# ---------------------------------------------------------------------------

from ... import db
from ...models import Carregamento


def atualiza_status(objeto: Carregamento, status: str, percent: int):
    """
    Atualiza o objeto Carregamento com o status e porcentagem fornecida.

    Parâmetros de entrada:
        objeto: Carregamento
            objeto Carregamento para atualizar.
        status: str
            String com o status do carregamento.
        percent: int
            Inteiro entre 0 a 100 contendo quanto ja foi feito da pesquisa.

    Parâmetros de saída:
        nenhum
    """

    objeto.status = status
    objeto.percent = percent
    db.session.add(objeto)
    db.session.commit()
