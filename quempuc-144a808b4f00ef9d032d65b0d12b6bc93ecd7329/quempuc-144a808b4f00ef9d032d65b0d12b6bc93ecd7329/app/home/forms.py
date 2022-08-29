from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class SearchForm(FlaskForm):
	busca = StringField('Busca', validators=[DataRequired()])
	submit_id = SubmitField('Buscar')