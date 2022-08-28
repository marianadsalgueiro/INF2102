from flask import render_template, url_for, flash, redirect
from flask_login import login_required, current_user

from . import user
from .forms import NewDataForm, escolhas_possiveis


def coletar_palavras_chave(nome):
    """
    Coleta as palavras chave daquele professor/orientador
    :param nome: Nome do professor/orientador
    :return: lista de dicionarios contendo as informacoes no formato
        [{"id": <int>, "palavra": <string>}, ...]
    """

    # TODO: consultar o banco

    ret = [
        {'id': 123, 'palavra': "Palavra 1 do %s" % nome},
        {'id': 321, 'palavra': "Palavra 2"},
        {'id': 1,   'palavra': "Palavra 3"},
        {'id': 54,  'palavra': "Palavra 4"},
    ]

    return ret


def coletar_laboratorios(nome):
    """
    Coleta os laboratórios daquele professor/orientador
    :param nome: Nome do professor/orientador
    :return: Lista de dicionarios contendo as informações de cada laboratorio, contendo pelo menos
        uma chave "id" e uma "nome"
    """

    # TODO: consultar o banco
    ret = [
        {"id": 123, "nome": "Laboratório 1", "departamento": "Departamento 1"},
        {"id": 987, "nome": "Laboratório 2", "departamento": "Departamento 2"},
        {"id": 741, "nome": "Laboratório 3", "departamento": "Departamento 3"},
        {"id": 4444, "nome": "Lab de %s" % nome, "departamento": "Algum departamento"},
    ]

    return ret


@user.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    nome_usuario = current_user.nome    # tambem pode ser pego do session['nome_usuario']

    # conteudo a ser exibido na pagina
    # a chave do dicionario deve ser a mesma que do dicionario de escolhas possiveis (nome no banco)
    # cada conteudo dentro do conteudo deve ser uma lista de dicionarios, em que cada dicionario
    # contem as informacoes.

    # exemplo:
    # conteudo['palavra_chave'][0] = {"id": 123, "palavra": "minha palavra"}
    # conteudo['laboratorio'][1] = {"id": 321, "nome: "meu lab", "departamento": "meu dep"}

    conteudo = {
        'palavra_chave': coletar_palavras_chave(nome_usuario),
        'laboratorio': coletar_laboratorios(nome_usuario)
    }

    # quais colunas devem ser exibidas de cada departamento.
    # o id nunca sera mostrado
    # cada string sera inserida no HTML as-is, exceto com uma capitalização na primeira letra
    # o primeiro da lista deve ser o identificador visual (ou seja, o seu "nome")
    abas = {
        'palavra_chave': ['palavra'],
        'laboratorio': ['nome', 'departamento']
    }

    return render_template('user/perfil.html',
                           conteudo=conteudo,
                           escolhas=escolhas_possiveis,     # dicionario {'nome_banco': 'nome_bonito'}
                           abas=abas)


@user.route("/remover/<string:tipo>/<int:pk_id>", methods=['GET', 'POST'])
@login_required
def remover_informacao(tipo: str, pk_id: int):

    if tipo not in escolhas_possiveis:
        # tipo impossivel?
        return render_template('errors/error.html')

    print("Removendo %s com id %d" % (tipo, pk_id))
    # TODO: remover do banco

    flash("Removida %s" % escolhas_possiveis[tipo], 'success')
    return redirect(url_for('user.perfil'))


@user.route('/novaInformacao', methods=['GET', 'POST'])
@login_required
def nova_informacao():
    form = NewDataForm()

    if form.validate_on_submit():
        # TODO: adicionar no banco
        flash('%s "%s" adicionado(a) com sucesso' % (
            escolhas_possiveis[form.tipo.data], form.informacao.data), 'success')
        return redirect(url_for('user.perfil'))

    return render_template('user/novaInformacao.html', form=form)
