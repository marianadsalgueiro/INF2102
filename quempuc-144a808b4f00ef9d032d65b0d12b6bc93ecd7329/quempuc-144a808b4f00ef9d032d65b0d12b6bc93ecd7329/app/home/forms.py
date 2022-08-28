# ---------------------------------------------------------------------------
# Author: Mariana Salgueiro
# ---------------------------------------------------------------------------

from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class SearchForm(FlaskForm):
	busca = StringField('Busca', validators=[DataRequired()])
	#ordenacao = SelectField("", choices=[('0', 'Ordem alfabética no nome de professores')], default='0')
	submit_id = SubmitField('Buscar')