from os import getenv, path, urandom
from dotenv import load_dotenv


class Settings:
    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir, '.env'))

    # Flask Settings
    SECRET_KEY = getenv("SECRET_KEY", "{{ random_ascii_string(32) }}")
    PORT = getenv("PORT", 80)
    DEBUG = getenv("DEBUG", False)
    TESTING = getenv("TESTING", False)
    ENV = getenv("ENV", "production")

    # APP Settings
    TITLE = getenv("TITLE", "{{ cookiecutter.project_title }}")
    DESC = getenv("DESC", "{{ cookiecutter.project_desc }}")
    SITE_URL = getenv("SITE_URL", "{{ cookiecutter.site_url }}")

    # Database Settings
    SQLALCHEMY_DATABASE_URI = getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///" + path.join(basedir, "{{ cookiecutter.sqlite_database_name }}.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # Mail Settings
    MAIL_SERVER = getenv("MAIL_SERVER", "{{ cookiecutter.mail_server }}")
    MAIL_PORT = getenv("MAIL_PORT", {{ cookiecutter.mail_port }})
    MAIL_USE_TLS = getenv("MAUL_USE_TLS", True)
    MAIL_USERNAME = getenv("MAIL_USERNAME", "{{ cookiecutter.mail_username }}")
    MAIL_PASSWORD = getenv("MAIL_PASSWORD", "{{ cookiecutter.mail_password }}")

settings = Settings()
