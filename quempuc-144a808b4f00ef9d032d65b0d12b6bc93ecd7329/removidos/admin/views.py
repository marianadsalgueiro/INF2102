# from flask import render_template, url_for, flash, redirect, session, request
# from flask_login import login_required
# from . import admin
# from .. import db, verifica_admin
# from wordcloud import WordCloud
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import os
# import glob
# import random
# from ..models import Frequencia_Termos, Busca, Usuario


# @admin.route('/paineladmin', methods=['GET', 'POST'])
# @login_required
# def dashboard():
#     verifica_admin()
#     rand = random.random()

#     for filename in glob.glob("./app/static/images/*"):
#         if 'wordcloud' in filename:
#             os.remove(filename)

#     palavras = Frequencia_Termos.query.all()

#     if not palavras:
#         iniciando_wordcloud = Frequencia_Termos(pk_palavra='begin', count=1)

#         try:
#             db.session.add(iniciando_wordcloud)
#             db.session.commit()
#         except Exception as e:
#             print(e)
#             db.session.rollback()

#         palavras = Frequencia_Termos.query.all()

#     d = {}
#     for i in range(0,len(palavras)):
#         d[palavras[i].pk_palavra] = palavras[i].count

#     #Generating wordcloud. Relative scaling value is to adjust the importance of a frequency word.
#     #See documentation: https://github.com/amueller/word_cloud/blob/master/wordcloud/wordcloud.py
#     wordcloud = WordCloud(width=800,height=400,max_words=1628,relative_scaling=0.5,normalize_plurals=False).generate_from_frequencies(d)

#     plt.figure(figsize=(13,8))
#     plt.imshow(wordcloud, interpolation='bilinear')
#     plt.axis("off")
#     plt.savefig('./app/static/images/wordcloud'+str(rand)+'.png', bbox_inches = 'tight', pad_inches = 0)
    
#     return render_template('admin/dashboard.html', url='../static/images/wordcloud'+str(rand)+'.png', palavras = palavras)


# @admin.route('/paineladmin/excluir-palavra/<palavra>', methods=['GET', 'POST'])
# @login_required
# def apaga_palavra(palavra):
#     verifica_admin()
#     try:
#         Frequencia_Termos.query.filter(Frequencia_Termos.pk_palavra==palavra).delete()
#         db.session.commit()
#     except Exception as e:
#         print(str(e))
#         db.session.rollback()
#         db.session.commit()

#     return redirect(url_for('admin.dashboard'))


# @admin.route('/logs')
# @login_required
# def logs():
#     verifica_admin()
#     try:
#         buscas = [x for x in Busca.query.all() if x.ip != '127.0.0.1']
#         return render_template('admin/logs.html', buscas=buscas)
#     except Exception as e:
#         print("Erro!", e)
#         return render_template('errors/error.html')


# @admin.route('/usuarios')
# @login_required
# def lista_usuarios():
#     verifica_admin()

#     usuarios = [
#         {'nome': x.nome,
#          'email': x.pk_email,
#          'autorizado': x.autorizado,
#          'admin': x.admin
#          } for x in Usuario.query.all()
#     ]

#     return render_template('admin/users.html', usuarios=usuarios)


# @admin.route('/usuarios/autorizar/<email>')
# @login_required
# def autorizar_usuario(email):
#     verifica_admin()

#     print("Autorizando email: ", email)

#     usuario = Usuario.query.get_or_404(email)
#     usuario.autorizado = True

#     try:
#         db.session.commit()
#     except Exception as e:
#         print("Erro! ", e)
#         db.session.rollback()

#     return redirect(url_for('admin.lista_usuarios'))


# @admin.route('/usuarios/remover/<email>')
# @login_required
# def remover_usuario(email):
#     verifica_admin()

#     print("Removendo email: ", email)

#     usuario = Usuario.query.get_or_404(email)

#     try:
#         db.session.delete(usuario)
#         db.session.commit()
#     except Exception as e:
#         print("Erro! ", e)
#         db.session.rollback()

#     return redirect(url_for('admin.lista_usuarios'))