# ---------------------------------------------------------------------------
# Author: Mariana Salgueiro
# ---------------------------------------------------------------------------

from flask import render_template, jsonify, request, flash, redirect, url_for

import logging
import difflib
import json
from os import path, remove
from threading import Thread

from .. import termos
from .. import get_db, db, decoded_id
from ..utils import registro_busca, registro_frequencia
from ..models import Carregamento
from . import home
from .forms import SearchForm
from .auxiliares import functions
from .auxiliares import pesquisa_index

# quando True, os dados enviados a pagina serao salvos em um arquivo json
DUMP = True

# Inicialização da variável que guarda o logger do módulo
logger = logging.getLogger(__name__)

# path para os arquivos json de pesquisa
PATH_PESQUISA = path.join(path.dirname(__file__), 'pesquisas', '%s.json')


@home.route('/', methods=['GET','POST'])
def index():
	"""
	Esta função carrega a página inicial da pesquisa.
	Se o formulário foi preenchido, ou seja, o usuário iniciou a pesquisa, será retornado um json contendo o código da pesquisa.
	Se tiver um parâmetro "status=<int>" na url, sera retornado um json contendo o status atual da pesquisa.
	Se tiver um parâmetro "finalizado=<int>" na url, a página final com resultados será exibida.

	Parâmetros de entrada:
		Formulário enviado através de POST em browser.

    Parâmetros de saída:
        Renderização do template da página inicial.
	"""

	form = SearchForm()

	# caso ele tenha iniciado a pesquisa
	if form.validate_on_submit():
		string_buscada = form.busca.data
		# criando novo carregamento
		novo_carregamento = Carregamento(status='Iniciando carregamento', percent=5,
										 busca=string_buscada)
		# colocando ele no banco
		db.session.add(novo_carregamento)
		db.session.commit()
		db.session.refresh(novo_carregamento)  # atualizando para pegar o seu id

		# criando e iniciando a thread
		thread = Thread(target=pesquisa_index.pesquisa_index, args=(string_buscada, novo_carregamento.id))
		print("Iniciando a thread da pesquisa index [%s] com id [%s]" % (string_buscada, novo_carregamento.id))
		thread.start()

		# salva nas estatisticas
		# registro_busca(string_buscada)
		# registro_frequencia(string_buscada)

		# retorna a pagina como esta, porem agora com o codigo
		return render_template('home/index.html', form=form, codigo=novo_carregamento.id, busca=string_buscada)

	# caso ele esteja so qurendo saber o status da pesquisa
	if request.args.get('status') is not None:
		try:
			token = int(request.args.get('status'))
			# puxando as informações do banco
			o = Carregamento.query.filter_by(id=token).first()
			return jsonify({'status': o.status, 'percent': o.percent})

		except Exception as e:
			print("Erro ao carregar a pagina index: ", str(e))
			# flash("Erro ao carregar a sua pesquisa, tente novamente mais tarde [%s]" % str(e))
			return redirect(url_for('home.index'))

	# caso ele esteja querendo os resultados prontos
	if request.args.get('finalizado') is not None:
		token = int(request.args.get('finalizado'))
		try:
			o = Carregamento.query.filter_by(id=token).first()
			string_buscada = o.busca
			if o is None:
				raise Exception("O token aponta para um objeto invalido [%s]" % token)

			filename = PATH_PESQUISA % token
			with open(filename, 'r') as f:
				ret = json.load(f)
				if type(ret) == str or 'dados' not in ret:
					raise Exception("Arquivo json invalido")

			# pegando os dados
			artigos, livros, capitulos, teses, disciplinas, bios = ret['dados']
			nomes = ret['nomes']
			matches = ret['matching']

			# verificando se nao tem algum dado
			if not artigos and not livros and not capitulos and not teses and not disciplinas and not bios:
				return render_template('errors/notfound.html', busca=string_buscada, matching=matches)

			# removendo o objeto do banco de dados
			db.session.delete(o)
			db.session.commit()
			remove(filename)

			# retornando a pagina final

			return render_template('home/index.html', form=form, dados=True,
								   artigos=artigos, capitulos=capitulos, teses=teses,
								   disciplinas=disciplinas, bios=bios, busca=string_buscada, 
								   matching=matches, nomes=nomes)
		except Exception as e:
			print("Erro ao carregar a pagina index: ", str(e))
			# flash("Erro ao carregar a sua pesquisa, tente novamente mais tarde [%s]" % str(e))
			return redirect(url_for('home.index'))

	# caso final, se ele ainda nao fez nada, carrega a pagina normalmente
	return render_template("home/index.html", form=form)


@home.route('/_loading/<int:codigo>', methods=['GET'])
def loading(codigo: int):
	"""
	Carrega as informações do loading da pesquisa.
	Se a pesquisa foi finalizada, os dados da pesquisa serão retornados em vez disso.

	Parâmetros de entrada:
		codigo: int 
			Id da pesquisa na tabela de carregamento.

    Parâmetros de saída:
        ret: json
			JSON contendo as informações.
	"""

	# puxa as informacoes
	o = Carregamento.query.filter_by(id=codigo).first()

	if o is None:
		return jsonify({})

	# coleta os dados
	ret = {
		"percent": o.percent,
		"status": o.status
	}

	return jsonify(ret)


@home.route('/sobrenos', methods=['GET','POST'])
def sobre():
	"""
	Carrega as informações da página sobre.

	Parâmetros de entrada:
		nenhum

    Parâmetros de saída:
        Renderização do template da página de sobre.
	"""
	return render_template("home/sobre.html")


@home.route('/faq', methods=['GET','POST'])
def faq():
	"""
	Carrega as informações da página FAQ.

	Parâmetros de entrada:
		nenhum

    Parâmetros de saída:
        Renderização do template da página de FAQ.
	"""
	return render_template("home/faq.html")
