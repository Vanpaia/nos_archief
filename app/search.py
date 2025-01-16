from flask import current_app
from datetime import date

def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)

def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        query={'multi_match': {'query': query, 'fields': ['*']}},
        from_=(page - 1) * per_page,
        size=per_page)
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']

def query_detail(index, query, page, per_page, category=None, start=None, end=None, fields=['*']):
    if not current_app.elasticsearch:
        return [], 0
    filters = []
    filters.append({'multi_match': {'query': query, 'fields': fields}})
    if not start and not end:
        pass
    else:
        if not start:
            start = current_app.config['START_DATE']
        elif not end:
            end = str(date.today())
        filters.append({'range': {'publish_timestamp': {"gte": start, "lte": end}}})
    if category:
        filters.append({'match': {'category': category}})
    search = current_app.elasticsearch.search(
        index=index,
        query={'bool': {'must': filters}},
        from_=(page - 1) * per_page,
        size=per_page)
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']


def api_query(index, query, page, per_page, category=None, start=None, end=None, fields=['*']):
    if not current_app.elasticsearch:
        return [], 0
    filters = []
    if query != "":
        filters.append({'multi_match': {'query': query, 'fields': fields}})
    if not start and not end:
        pass
    else:
        if not start:
            start = current_app.config['START_DATE']
        elif not end:
            end = str(date.today())
        filters.append({'range': {'publish_timestamp': {"gte": start, "lte": end}}})
    if category:
        filters.append({'match': {'category': category}})
    search = current_app.elasticsearch.search(
        index=index,
        query={'bool': {'must': filters}},
        from_=(page - 1) * per_page,
        size=per_page)
    ids = [[hit['_source']['title'], hit['_source']['category'].split(" | "), hit['_source']['publish_timestamp']] for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']