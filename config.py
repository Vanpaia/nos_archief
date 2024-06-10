import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

class Config(object):
    SECRET_KEY = config['DEFAULT']['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = config['DEFAULT']['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = config['DEFAULT']['POSTS_PER_PAGE']
    ELASTICSEARCH_URL = config['DEFAULT']['ELASTICSEARCH_URL']
    ELASTICSEARCH_USERNAME = config['DEFAULT']['ELASTICSEARCH_USERNAME']
    ELASTICSEARCH_PASSWORD = config['DEFAULT']['ELASTICSEARCH_PASSWORD']
    ELASTICSEARCH_CERT = config['DEFAULT']['ELASTICSEARCH_CERT']