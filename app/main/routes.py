from flask import render_template, g
from app.main.forms import SearchForm

from app import db
from app.main import bp


@bp.before_app_request
def before_request():
    g.search_form = SearchForm()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Home')