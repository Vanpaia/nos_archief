from flask import render_template, g, redirect, url_for, current_app, request, jsonify, make_response
from flask_limiter import RequestLimit
from datetime import datetime, timedelta
from calendar import monthrange
from sqlalchemy import Date, Time, cast
import json
from math import ceil

from app import db, limiter
from app.api import bp

from app.main.forms import SearchForm, ArchiveForm, AdvancedSearchForm
from app.models import RSSCategory, RSSArticle
from app.search import  api_query


def api_error_responder(rate_limit):
    return make_response(
        jsonify(error=429, description="ratelimit exceeded", limit=f"{rate_limit.limit}"),
        429)

@bp.route('/api', methods=['GET', 'POST'])
def overview():
    return render_template('api/overview.html', title='API')

@bp.route('/api/v1', methods=['GET', 'POST'])
@limiter.limit("5000 per day, 1000 per hour, 100 per minute", on_breach=api_error_responder)
def api_call():
    #Pulling the data from the URL for further use
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    rsscategory = request.args.get('categorie', None)
    title_only = request.args.get('title')
    if title_only == 'True':
        fields = ['title']
    else:
        fields = ['*']
    query = request.args.get('q', '')
    articles, total = api_query(index="rss_article", query=query, page=page, per_page=limit, category=rsscategory, start=start_date, end=end_date, fields=fields)
    api_response = jsonify({"result_amount": total,
                            "result_pagination": {
                                "limit": limit,
                                "page": page,
                                "max_page": ceil(total/limit)
                            },
                            "result_query": {
                                "search": query,
                                "start_date": start_date,
                                "end_date": end_date,
                                "categories": None if rsscategory is None else rsscategory.split(),
                                "title_only": title_only
                            },
                            "results": articles})
    return api_response