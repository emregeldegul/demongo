from os import getenv, path, urandom
from dotenv import load_dotenv


class Settings:
    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir, '.env'))

    # Flask Settings
    SECRET_KEY = getenv("SECRET_KEY", urandom(24))
    PORT = getenv("PORT", 80)
    DEBUG = getenv("DEBUG", False)
    TESTING = getenv("TESTING", False)
    ENV = getenv("ENV", "production")

    # APP Settings
    TITLE = getenv("TITLE", "Demongo")
    BRIEF = getenv("BRIEF", "A Simple Structure For the Flask Framework")
    SITE_URL = getenv("SITE_URL", "localhost")

    # Database Settings
    SQLALCHEMY_DATABASE_URI = getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///" + path.join(basedir, "demongo.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # Mail Settings
    MAIL_SERVER = getenv("MAIL_SERVER", "smtp.googlemail.com")
    MAIL_PORT = getenv("MAIL_SERVER", 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = getenv("MAIL_PASSWORD", "")


settings = Settings()
