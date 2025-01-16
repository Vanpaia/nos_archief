from flask import Flask, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address

from elasticsearch import Elasticsearch

import os
import logging
from logging.handlers import RotatingFileHandler

from config import Config


def default_error_responder(request_limit: RequestLimit):
    return make_response(
        render_template("429.html"),
        429
    )

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
moment = Moment()
limiter = Limiter(
    get_remote_address,
    on_breach=default_error_responder
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    moment.init_app(app)
    limiter.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']],
                                      ca_certs=app.config['ELASTICSEARCH_CERT'],
                                      basic_auth=(app.config['ELASTICSEARCH_USERNAME'],
                                                  app.config['ELASTICSEARCH_PASSWORD'])) \
        if Config.ELASTICSEARCH_URL else None

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/nos_archief.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('NOS Archief startup')

    return app

from app import models
