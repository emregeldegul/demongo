from os import path, urandom

BASEDIR = path.abspath(path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(BASEDIR, 'demongo.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "demongo"