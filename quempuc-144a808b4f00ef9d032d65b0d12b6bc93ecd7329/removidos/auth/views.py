# from flask import render_template, url_for, flash, redirect, session, abort
# from flask_login import login_required, login_user, logout_user, current_user
# from werkzeug.security import generate_password_hash, check_password_hash

# from . import auth
# from .. import db, verifica_admin
# from ..models import Professor
# from .forms import *

# import re
# import secrets


# def coletar_nomes_possiveis():
#     """
#     Coleta todos os nomes possiveis da base de dados
#     :return: uma lista contendo os nomes dos professores/auxiliares
#     """

#     nomes = db.session.query(
#         Professor.nome
#     ).filter(
#         Professor.situacao != 'DEMITIDO',
#         Professor.tipo == 'Professor'
#     ).order_by(
#         Professor.nome
#     ).all()

#     # nomes é uma lista onde cada elemento é uma tupla com um elemento (nome,)
#     return [n[0] for n in nomes]


# def pegar_professor_usando_lattes(lattes: str):
#     """
#     Faz uma consulta no postgres usando o lattes do professor para conseguir o email
#     :param lattes: Link lattes do professor, ou só o id
#     :return: email do professor, ou None caso não encontre nenhum professor
#     """

#     # pegando o id do allegro

#     match = re.match(r"(http:\/\/lattes\.cnpq\.br/)?([0-9]+)", lattes)
#     if match is None:
#         return None     # o link eh invalido

#     groups = match.groups()

#     if len(groups) == 1 or len(groups) == 2:
#         numLattes = groups[1]
#     else:
#         return None     # algum erro ocorreu

#     prof = Professor.query.filter(
#         Professor.lattes == numLattes,
#         Professor.situacao != "DEMITIDO"
#     ).first()

#     return prof


# def esconder_email(email: str):
#     """
#     Esconde parte do email em asteriscos
#     :param email: string completa do email
#     :return: string com email parcialmente escondido
#     """

#     p = email[:2]
#     indiceArroba = email.find('@')
#     return p + '*' * (indiceArroba - 2) + email[indiceArroba:]


# def criar_token():
#     """
#     Gera um token forte, formada por 6 letras, 3 números e 3 símbolos, colocados
#     em lugares aleatórios, escolhidos de forma aleatória.
#     :return: string da token
#     """
#     alfabeto = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
#     letras = [secrets.choice(alfabeto) for _ in range(6)]
#     numeros = [secrets.choice('0123456789') for _ in range(3)]
#     simbolos = [secrets.choice('!@#$%*+') for _ in range(3)]
#     token = []
#     escolhas = [0, 1, 2]
#     for _ in range(12):
#         e = secrets.choice(escolhas)
#         if e == 0:
#             token.append(letras.pop())
#             if not letras:
#                 escolhas.remove(0)
#         elif e == 1:
#             token.append(numeros.pop())
#             if not numeros:
#                 escolhas.remove(1)
#         else:
#             token.append(simbolos.pop())
#             if not simbolos:
#                 escolhas.remove(2)

#     return ''.join(token)


# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():

#         # check whether user exists in the database and whether
#         # the password entered matches the password in the database
#         usuario = Usuario.query.filter_by(pk_email=form.email.data).first()
#         if usuario is not None and check_password_hash(usuario.senha, form.senha.data):
#             if usuario.autorizado:
#                 login_user(usuario)
#                 session["nome_usuario"] = usuario.nome

#                 if usuario.admin:
#                     return redirect(url_for('admin.dashboard'))
#                 else:
#                     return redirect(url_for('user.perfil'))

#             else:
#                 flash("Sua conta ainda não foi autorizada. Por favor aguarde.", 'warning')

#         # when login details are incorrect
#         else:
#             flash('Email ou senha incorretos.', 'danger')

#     # load login template
#     return render_template('auth/login.html', form=form)


# @auth.route('/register/manual', methods=['GET', 'POST'])
# def registerManual():
#     form = RegistroManualForm()

#     # preenchendo o campo de nomes com os nomes possiveis
#     # nomes_possiveis = coletar_nomes_possiveis()
#     # form.nome.choices = [('', '')] + [(nome, nome) for nome in nomes_possiveis]

#     if form.validate_on_submit():
#         # registrando o usuario na base de dados
#         novo_usuario = Usuario(
#             pk_email=form.email.data,
#             nome=form.nome.data,
#             senha=generate_password_hash(form.senha.data),
#             admin=False,
#             autorizado=False
#         )
#         # adiciona o usuario no banco
#         db.session.add(novo_usuario)
#         db.session.commit()

#         flash("Sua conta foi criada com sucesso. Aguarde até ela ser manualmente verificada e autorizada.")
#         return redirect(url_for('auth.login'))

#     return render_template('auth/registerManual.html', form=form)


# @auth.route('/register/auto', methods=['GET', 'POST'])
# def registerAuto():
#     form = RegistroAuto()

#     if form.validate_on_submit():
#         prof = pegar_professor_usando_lattes(form.lattes.data)
#         # verificando se existe o professor
#         if prof is None:
#             flash("Lattes não encontrado.", 'danger')
#             return render_template('auth/registerAuto.html', form=form)

#         # verifica se o email de autorizacao ja foi enviado pra ele
#         if Usuario.query.filter(
#             Usuario.pk_email == prof.email,
#             not Usuario.autorizado,
#             Usuario.token is not None
#         ).first() is not None:
#             flash("Essa conta aguarda validação por email.", 'warning')
#             return render_template('auth/registerAuto.html', form=form)

#         # se ja houver um usuario com esse email
#         if Usuario.query.filter_by(pk_email=prof.email).first() is not None:
#             flash("Essa conta já existe.", 'danger')
#             return render_template('auth/registerAuto.html', form=form)

#         # criando conta
#         token = criar_token()

#         # TODO: enviar email
#         print("===TOKEN===: ", token)
#         print("===Link===: ", url_for('auth.trocar_senha', token=token))

#         novo_usuario = Usuario(
#             pk_email=prof.email,
#             nome=prof.nome,
#             senha="",       # nenhuma senha consegue dar match com "" devido ao hash
#             admin=False,
#             autorizado=True,
#             token=token
#         )
#         db.session.add(novo_usuario)
#         db.session.commit()

#         flash("Para finalizar o cadastro, siga as instruções que foram enviadas para o email %s."
#               % esconder_email(prof.email), 'info')
#         return redirect(url_for('auth.login'))

#     return render_template('auth/registerAuto.html', form=form)


# @auth.route('/logout', methods=['GET', 'POST'])
# @login_required
# def logout():
#     """
#     Controla o logout de um usuário
#     """
#     logout_user()
#     flash('Você fez logout com sucesso.', 'success')
#     return redirect(url_for('home.index'))


# @auth.route('/login/esqueci_senha', methods=['GET', 'POST'])
# def esqueci_senha():
#     """
#     Controla a página de esqueci senha
#     """
#     form = EsqueciSenhaForm()

#     if form.validate_on_submit():
#         email = form.email.data

#         user = Usuario.query.filter(
#             Usuario.pk_email == email
#         ).first()

#         # se houver algum usuario com aquele email
#         if user is not None:
#             # gerando token
#             token = criar_token()
#             user.token = token

#             #TODO: enviar email
#             print("===TOKEN===", token)
#             print("===Link===: ", url_for('auth.trocar_senha', token=token))

#             db.session.commit()

#         flash("Siga as instruções que foram enviadas para o email, caso exista"
#               " uma conta cadastrada com este email.")
#         return redirect(url_for('auth.login'))

#     return render_template('auth/esqueciSenha.html', form=form)


# @auth.route('/register/trocar_senha/<string:token>', methods=['GET', 'POST'])
# def trocar_senha(token: str):
#     """
#     Controla a pagina de alterar a senha

#     Há três caminhos para chegar nesta página:
#         1: Um novo usuario criado automaticamente, acessando utilizando seu token
#         2: Um usuário existente (autorizado ou nao) logado querendo trocar sua senha,
#             em que o token será "-" (um token invalido)
#         3: Um usuário existente (autorizado ou nao) que esqueceu sua senha, acessando
#             utilizando seu token

#     Caso 1 e 3: é utilizado o seu token para saber quem ele é
#     Caso 2: é usado sua sessão para saber quem ele é
#     """

#     # valida o token ou usuario
#     usuario = current_user
#     if not usuario.is_authenticated:     # o usuario nao esta logado
#         usuario = Usuario.query.filter_by(token=token).first()

#     if usuario is None:     # o usuario nao tem token/possui token invalido
#         abort(403)

#     # nesse ponto, "usuario" é o usuario verdadeiro

#     form = NovaSenhaForm()
#     if form.validate_on_submit():
#         senha = form.senha.data
#         usuario.senha = generate_password_hash(senha)
#         if usuario.token is not None:
#             usuario.token = None    # limpando o token

#         db.session.commit()

#         flash("Senha atualizada com sucesso.", 'success')
#         if current_user.is_authenticated:
#             return redirect(url_for('user.perfil'))
#         else:
#             return redirect(url_for('auth.login'))

#     return render_template('auth/trocarSenha.html', form=form, nome_usuario=usuario.nome)
