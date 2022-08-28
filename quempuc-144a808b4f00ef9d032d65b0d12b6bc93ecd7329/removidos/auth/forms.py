# Local imports
from ..models import Usuario
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError


class LoginForm(FlaskForm):
    """ Classe de formulário para login """
    email = StringField(validators=[DataRequired(), Email(message='E-mail inválido'),
                                    Length(max=60, message='Campo não pode conter mais de 60 caracteres')])

    senha = PasswordField(validators=[DataRequired()])

    submit = SubmitField('Entrar')


class RegistroManualForm(FlaskForm):
    """
    Classe de formulário para registro manual, quando nao existe o email
    """

    # as escolhas de nomes serao preenchidas dinamicamene na view
    nome = StringField("Nome", validators=[DataRequired(message="Nome é um campo obrigatório")])


    email = StringField('Email', validators=[DataRequired(message="Email é um campo obrigatório."),
                                             Email(message="Email inválido"),
                                             Length(max=60, message="Número de caracteres(60) excedido.")])

    senha = PasswordField('Senha',
                          validators=[DataRequired(message="Senha é um campo obrigatório."),
                                      # Regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)([a-zA-Z\d._\-]){8,}$",
                                      # message='A senha inserida não está conforme o indicado.')]
                                      Length(min=8, message="Senha muito curta, deve ter pelo menos 8 caracteres")
                                      ]
                          )

    senhaConfirma = PasswordField('Confirme sua senha',
                                  validators=[DataRequired(message="Confirmar senha é um campo obrigatório."),
                                              EqualTo('senha', message="As senhas não são iguais.")])

    submit = SubmitField('Confirmar')

    def validate_email(self, field):
        """Valida para ver se o email ja nao foi usado"""
        user = Usuario.query.filter_by(pk_email=field.data).first()
        if user is not None:
            raise ValidationError('Email já cadastrado.')

    def validate_nome(self, field):
        """Valida para ver se o nome ja nao foi usado"""
        if Usuario.query.filter_by(nome=field.data).first() is not None:
            raise ValidationError('Nome já cadastrado.')

        if field.data == '':
            raise ValidationError('Selecione um nome da lista')


class RegistroAuto(FlaskForm):
    """
    Formulario para registros cujo email já está no banco
    """
    lattes = StringField(
        'Link ou ID Lattes',
        validators=[
            DataRequired(message="Email é um campo obrigatório."),
            Regexp(regex="(http:\/\/lattes\.cnpq\.br\/)?[0-9]+", message="URL inválida.")
        ],
        render_kw={"placeholder": "http://lattes.cnpq.br/1234567890 ou 1234567890"},
    )
    submit = SubmitField('Confirmar')


class EsqueciSenhaForm(FlaskForm):
    """
    Formulario para pedidos de esqueci a senha
    """
    email = StringField('Email', validators=[DataRequired(message="Email é um campo obrigatório."),
                                             Email(message="Email inválido"),
                                             Length(max=60, message="Número de caracteres(60) excedido.")])
    submit = SubmitField('Enviar')


class NovaSenhaForm(FlaskForm):
    """
    Formulario para novas senhas
    """
    senha = PasswordField('Senha',
                          validators=[DataRequired(message="Senha é um campo obrigatório."),
                                      Length(min=8, message="Senha muito curta, deve ter pelo menos 8 caracteres")
                                      ]
                          )

    senhaConfirma = PasswordField('Confirme sua senha',
                                  validators=[DataRequired(message="Confirmar senha é um campo obrigatório."),
                                              EqualTo('senha', message="As senhas não são iguais.")])

    submit = SubmitField('Confirmar')
