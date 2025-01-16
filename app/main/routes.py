from flask import render_template, g, redirect, url_for, current_app, request, jsonify
from flask_wtf import form
from datetime import datetime, timedelta
from calendar import monthrange
from sqlalchemy import Date, Time, cast

from app import db
from app.main import bp

from app.main.forms import SearchForm, ArchiveForm, AdvancedSearchForm
from app.models import RSSCategory, RSSArticle
from app.summary import summarize


@bp.before_app_request
def before_request():
    g.search_form = SearchForm()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Index')

@bp.route('/archief', methods=['GET', 'POST'])
def archief():
    filter_period = request.args.get('period')
    if not filter_period:
        filter_date = datetime.now()
    else:
        filter_date = datetime.strptime(request.args.get('date'), '%Y-%m-%d')
    if filter_period == 'week':
        start_date = filter_date.date() - timedelta(days=filter_date.weekday())
        end_date = filter_date.date() + (timedelta(days=(6 - filter_date.weekday())))
    elif filter_period == 'maand':
        month_length = monthrange(filter_date.year, filter_date.month)
        start_date = filter_date.date() - timedelta(days=(filter_date.day - 1))
        end_date = filter_date.date() + timedelta(days=(month_length[1] - filter_date.day))
    else:
        start_date = filter_date.date()
        end_date = filter_date.date()
    query = RSSArticle.query.filter(cast(RSSArticle.publish_timestamp,Date) >= start_date).filter(cast(RSSArticle.publish_timestamp,Date) <= end_date).order_by(cast(RSSArticle.publish_timestamp,Date)).order_by(cast(RSSArticle.publish_timestamp,Time))
    filter_rsscategory = request.args.get('rsscategorie')
    if filter_rsscategory is None:
        pass
    elif filter_rsscategory == 'alles':
        pass
    else:
        query = query.filter(RSSArticle.categories.any(title=filter_rsscategory)).all()
    titles = []
    for title in query:
        titles.append(title.title)
    datepicker = ArchiveForm(date=filter_date, period=request.args.get('period'), rsscategory=request.args.get('rsscategorie'))
    if datepicker.validate_on_submit():
        return redirect(url_for('main.archief', date=datepicker.date.data, period=datepicker.period.data, categorie=datepicker.rsscategory.data))
    return render_template('archief.html', query=query, date=filter_date, start_date=start_date, end_date=end_date, datepicker=datepicker, titles=titles)

@bp.route('/geavanceerd_zoeken', methods=['GET', 'POST'])
def geavanceerd_zoeken():
    advanced_search = AdvancedSearchForm()
    if advanced_search.validate_on_submit():
        start_date = advanced_search.start_date.data
        end_date = advanced_search.end_date.data
        rsscategory = advanced_search.rsscategory.data
        query = advanced_search.query.data
        title_only = advanced_search.title_only.data
        return redirect(url_for('main.resultaten', q=query, title=title_only, categorie=rsscategory, start=start_date, end=end_date))
    return render_template('geavanceerd_zoeken.html', title='Geavanceerd Zoeken', form=advanced_search)

@bp.route('/resultaten', methods=['GET', 'POST'])
def resultaten():
    #Pulling the data from the URL for further use
    page = request.args.get('page', 1, type=int)
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    rsscategory = request.args.get('categorie')
    if rsscategory == 'alles':
        rsscategory = None
    title_only = request.args.get('title')
    print(title_only)
    if title_only == 'True':
        fields = ['title']
    else:
        fields = ['*']
    query = request.args.get('q')
    #Initialising and prepopulating search form
    advanced_search = AdvancedSearchForm()
    if advanced_search.validate_on_submit():
        new_start_date = advanced_search.start_date.data
        new_end_date = advanced_search.end_date.data
        new_rsscategory = advanced_search.rsscategory.data
        new_query = advanced_search.query.data
        new_title_only = advanced_search.title_only.data
        return redirect(url_for('main.resultaten', q=new_query, title=new_title_only, categorie=new_rsscategory, start=new_start_date, end=new_end_date))
    articles, total = RSSArticle.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'], rsscategory=rsscategory, start=start_date, end=end_date, fields=fields)
    next_url = url_for('main.resultaten', q=query, title=title_only, rsscategory=rsscategory, start=start_date, end=end_date, page=page+1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.resultaten', q=query, title=title_only, rsscategory=rsscategory, start=start_date, end=end_date, page=page-1) \
        if page > 1 else None
    return render_template('resultaten.html', title='Zoek Resultaten', articles=articles, total=total, form=advanced_search,
                               next_url=next_url, prev_url=prev_url)


@bp.route('/summarize', methods=['POST'])
def summarize_titles():
    return jsonify({'text': summarize(request.form.getlist('titles[]'))})