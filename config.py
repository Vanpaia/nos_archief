import os
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

class Config(object):
    SECRET_KEY = config['DEFAULT']['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = config['DEFAULT']['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATELIMIT_STORAGE_URI = "memcached://localhost:11211"
    RATELIMIT_DEFAULT = "500 per day, 100 per hour"
    POSTS_PER_PAGE = int(config['DEFAULT']['POSTS_PER_PAGE'])
    START_DATE = config['DEFAULT']['START_DATE']
    ELASTICSEARCH_URL = config['DEFAULT']['ELASTICSEARCH_URL']
    ELASTICSEARCH_USERNAME = config['DEFAULT']['ELASTICSEARCH_USERNAME']
    ELASTICSEARCH_PASSWORD = config['DEFAULT']['ELASTICSEARCH_PASSWORD']
    ELASTICSEARCH_CERT = config['DEFAULT']['ELASTICSEARCH_CERT']
    GEMINI_API = config['DEFAULT']["GEMINI_API"]
