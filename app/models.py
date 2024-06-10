from app import db
#from app.search import add_to_index, remove_from_index, query_index

from datetime import datetime


article_category = db.Table('category',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capture_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    title = db.Column(db.String(256), index=True)
    link = db.Column(db.String(128), index=True)
    image = db.Column(db.String(128))
    publish_timestamp = db.Column(db.DateTime, index=True)
    summary = db.Column(db.Text)

    categories = db.relationship(
        'NewsCategory', secondary=article_category,
        primaryjoin=(article_category.c.category_id == id),
        backref=db.backref('categories', lazy='dynamic'), lazy='dynamic')

class NewsCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)
    supercategory = db.Column(db.String(56), index=True)
    link = db.Column(db.String(128), index=True)

    articles = db.relationship(
        'Article', secondary=article_category,
        primaryjoin=(article_category.c.article_id == id),
        backref=db.backref('articles', lazy='dynamic'), lazy='dynamic')
