from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


escolhas_possiveis = {
    'laboratorio': 'Laboratório',
    'palavra_chave': 'Palavra-chave',
}


class NewDataForm(FlaskForm):

    escolhas = [(key, value) for key,value in escolhas_possiveis.items()]

    tipo = SelectField("Selecione o que será adicionado", choices=escolhas, default=escolhas[0][0])
    informacao = StringField("Digite a nova informação", validators=[DataRequired()])
    submit = SubmitField('Adicionar')
