from flask_login import UserMixin
from app import db, login_manager


class Busca(UserMixin, db.Model):
    __tablename__ = 'busca'

    pk_id = db.Column(db.Integer, primary_key=True)
    data_e_hora = db.Column(db.DateTime)
    ip = db.Column(db.String(20))
    sistema_operacional = db.Column(db.String(20))
    browser = db.Column(db.String(20))
    palavra_buscada = db.Column(db.String(50))
    professor_selecionado = db.Column(db.String(100))


class Frequencia_Termos(UserMixin, db.Model):
    __tablename__ = 'frequencia_termos'

    pk_palavra = db.Column(db.String(50), primary_key=True)
    count = db.Column(db.Integer)


class Carregamento(UserMixin, db.Model):
    __tablename__ = "carregamento"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    # identificador da pesquisa
    status = db.Column(db.String(100))                                  # status (texto) da pesquisa
    percent = db.Column(db.Integer)                                     # 0%-100% da pesquisa
    nome = db.Column(db.String(100))
    busca = db.Column(db.String(100))
    flagNome = db.Column(db.Integer)