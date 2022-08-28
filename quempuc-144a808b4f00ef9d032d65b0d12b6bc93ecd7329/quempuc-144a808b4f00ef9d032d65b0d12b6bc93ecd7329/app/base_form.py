from flask_wtf import FlaskForm

class NimaBaseForm(FlaskForm):
    class Meta:
        locales = ['pt', 'en']
