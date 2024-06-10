from app import db
#from app.search import add_to_index, remove_from_index, query_index

from datetime import datetime


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capture_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    title = db.Column(db.String(256), index=True)
    link = db.Column(db.String(128), index=True)
    image = db.Column(db.String(128))
    publish_timestamp = db.Column(db.DateTime, index=True)
    summary = db.Column(db.Text)
