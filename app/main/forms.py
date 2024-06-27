import wtforms
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, RadioField
from wtforms.validators import DataRequired

categories = [
    ("alles", "Alles"),
    ("algemeen", "Nieuws Algemeen"),
    ("binnenland", "Nieuws Binnenland"),
    ("buitenland", "Nieuws Buitenland"),
    ("politiek", "Nieuws Politiek"),
    ("economie", "Nieuws Economie"),
    ("opmerkelijk", "Nieuws Opmerkelijk"),
    ("koningshuis", "Nieuws Koningshuis"),
    ("cultuur en media", "Nieuws Cultuur en Media"),
    ("tech", "Nieuws Tech"),
    ("algemeen", "Sport Algemeen"),
    ("voetbal", "Sport Voetbal"),
    ("wielrennen", "Sport Wielrennen"),
    ("schaatsen", "Sport Schaatsen"),
    ("tennis", "Sport Tennis"),
    ("formule 1", "Sport Formule 1"),
    ("nieuwsuur", "Nieuwsuur"),
    ("NOS op 3", "NOS op 3"),
    ("NOS jeugdjournaal", "NOS Jeugdjournaal")
    ]

class SearchForm(FlaskForm):
    q = StringField('Zoeken', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)



class DateForm(FlaskForm):
    date = DateField('Datum', format='%Y-%m-%d')

class CategoryForm(FlaskForm):
    language = SelectField('Categorie', choices=categories)

class ArchiveForm(FlaskForm):
    date = wtforms.DateField('Datum', format='%Y-%m-%d')
    period = wtforms.RadioField('Periode', default='dag', choices=['dag', 'week', 'maand'], validate_choice=False)
    category = wtforms.SelectField('Categorie', choices=categories, validate_choice=False)
    submit = SubmitField('Zoeken')

class AdvancedSearchForm(FlaskForm):
    start_date = wtforms.DateField('Vanaf', format='%Y-%m-%d')
    end_date = wtforms.DateField('Tot', format='%Y-%m-%d')
    category = wtforms.SelectField('Categorie', choices=categories)
    query = wtforms.StringField('Zoektermen')
    title_only = wtforms.BooleanField('Alleen titel doorzoeken  ')
    submit = SubmitField('Zoeken')