from app import db
from app.search import add_to_index, remove_from_index, query_detail

from datetime import datetime
from sqlalchemy import Date, cast


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page, category=None, start=None, end=None, fields=['*']):
        ids, total = query_detail(cls.__tablename__, expression, page, per_page, category, start, end, fields)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = {}
        for i in range(len(ids)):
            when[ids[i]] = i
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

article_category = db.Table('article_category',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('news_category.id'), primary_key=True)
)


class Article(SearchableMixin, db.Model):
    __searchable__ = ['title', 'summary', 'publish_timestamp']
    id = db.Column(db.Integer, primary_key=True)
    capture_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    title = db.Column(db.String(256), index=True)
    link = db.Column(db.String(128), index=True)
    image = db.Column(db.String(128))
    publish_timestamp = db.Column(db.DateTime, index=True)
    summary = db.Column(db.Text)

    categories = db.relationship(
        "NewsCategory",
        secondary=article_category,
        back_populates='articles',
        cascade = "all, delete"
    )

    def to_date(self):
        return self.publish_timestamp.date()

    def to_time(self):
        return self.publish_timestamp.time()



class NewsCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)
    supercategory = db.Column(db.String(128), index=True)
    link = db.Column(db.String(128), index=True)

    articles = db.relationship(
        "Article",
        secondary=article_category,
        back_populates='categories',
        passive_deletes=True)
