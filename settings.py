import pathlib

from decouple import config

from app.helpers.sqlalchemy_helpers import DatabaseProvider, build_database_uri

# settings.py lives at the project root, so this is the root itself — the
# same directory as app/, migrations/, and wsgi.py.
BASE_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent


class Settings:
    # Flask Settings
    SECRET_KEY: str = config("SECRET_KEY", cast=str, default="supersecretkey")
    # Absolute, not "../static" relative to app/'s root_path: static/ lives
    # next to app/ (see app/__init__.py), not inside it.
    STATIC_FOLDER: str = config("STATIC_FOLDER", cast=str, default=str(BASE_DIR / "static"))

    # APP Settings
    APP_NAME: str = config("APP_NAME", cast=str, default="Demongo")
    APP_VERSION: str = config("APP_VERSION", cast=str, default="0.0.1")

    # Site Settings
    SITE_NAME: str = config("SITE_NAME", cast=str, default="Demongo Site")
    SITE_DESCRIPTION: str = config("SITE_DESCRIPTION", cast=str, default="This is the Demongo site.")
    SITE_URL: str = config("SITE_URL", cast=str, default="http://localhost:5000")

    # PostgreSQL Database Settings
    # Named to match Flask-Mail's MAIL_* convention below (_SERVER, _PORT,
    # _USERNAME, _PASSWORD) — unlike MAIL_*, these names are ours to choose,
    # so they follow the library's pattern instead of inventing a second one.
    POSTGRESQL_SERVER: str = config("POSTGRESQL_SERVER", cast=str, default="localhost")
    POSTGRESQL_PORT: int = config("POSTGRESQL_PORT", cast=int, default=5432)
    POSTGRESQL_USERNAME: str = config("POSTGRESQL_USERNAME", cast=str, default="postgres")
    POSTGRESQL_PASSWORD: str = config("POSTGRESQL_PASSWORD", cast=str, default="postgres")
    POSTGRESQL_DATABASE_NAME: str = config("POSTGRESQL_DATABASE_NAME", cast=str, default="demongo")

    # MySQL Database Settings
    MYSQL_SERVER: str = config("MYSQL_SERVER", cast=str, default="localhost")
    MYSQL_PORT: int = config("MYSQL_PORT", cast=int, default=3306)
    MYSQL_USERNAME: str = config("MYSQL_USERNAME", cast=str, default="root")
    MYSQL_PASSWORD: str = config("MYSQL_PASSWORD", cast=str, default="root")
    MYSQL_DATABASE_NAME: str = config("MYSQL_DATABASE_NAME", cast=str, default="demongo")

    # SQLite Database Settings
    SQLITE_DATABASE_NAME: str = config("SQLITE_DATABASE_NAME", cast=str, default="demongo.db")

    # SQLAlchemy Settings
    DATABASE_PROVIDER: DatabaseProvider = config(
        "DATABASE_PROVIDER", cast=lambda v: DatabaseProvider(v.lower()), default=DatabaseProvider.SQLITE
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = config("SQLALCHEMY_TRACK_MODIFICATIONS", cast=bool, default=False)

    # Mail Settings
    MAIL_SERVER: str = config("MAIL_SERVER", cast=str, default="")
    MAIL_PORT: int = config("MAIL_PORT", cast=int, default=587)
    MAIL_USE_TLS: bool = config("MAIL_USE_TLS", cast=bool, default=True)
    MAIL_USE_SSL: bool = config("MAIL_USE_SSL", cast=bool, default=False)
    MAIL_USERNAME: str = config("MAIL_USERNAME", cast=str, default="")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD", cast=str, default="")
    MAIL_DEFAULT_SENDER: str = config("MAIL_DEFAULT_SENDER", cast=str, default="no-reply@demongo.local")
    # No MAIL_SERVER means there's nowhere to send to, so suppress by default —
    # a fresh clone can then "send" mail with zero SMTP setup. Set MAIL_SERVER
    # (and this, explicitly, if you still want it suppressed) to send for real.
    MAIL_SUPPRESS_SEND: bool = config("MAIL_SUPPRESS_SEND", cast=bool, default=not MAIL_SERVER)

    # Redis Settings (shared by caching, rate limiting, and the RQ queue)
    REDIS_URL: str = config("REDIS_URL", cast=str, default="redis://localhost:6379/0")

    # Cache Settings
    CACHE_TYPE: str = config("CACHE_TYPE", cast=str, default="SimpleCache")
    CACHE_DEFAULT_TIMEOUT: int = config("CACHE_DEFAULT_TIMEOUT", cast=int, default=300)
    CACHE_REDIS_URL: str = config("CACHE_REDIS_URL", cast=str, default=REDIS_URL)

    # Rate Limit Settings
    RATELIMIT_STORAGE_URI: str = config("RATELIMIT_STORAGE_URI", cast=str, default="memory://")
    RATELIMIT_DEFAULT: str = config("RATELIMIT_DEFAULT", cast=str, default="200 per day;50 per hour")

    # Babel (i18n) Settings
    LANGUAGES: list[str] = config("LANGUAGES", cast=lambda v: [lang.strip() for lang in v.split(",")], default="en,tr")
    BABEL_DEFAULT_LOCALE: str = config("BABEL_DEFAULT_LOCALE", cast=str, default="en")
    BABEL_DEFAULT_TIMEZONE: str = config("BABEL_DEFAULT_TIMEZONE", cast=str, default="UTC")

    # Upload Settings
    MAX_CONTENT_LENGTH: int = config("MAX_CONTENT_LENGTH", cast=int, default=5 * 1024 * 1024)  # 5 MB
    UPLOAD_ALLOWED_EXTENSIONS: set[str] = config(
        "UPLOAD_ALLOWED_EXTENSIONS",
        cast=lambda v: {ext.strip().lower() for ext in v.split(",")},
        default="png,jpg,jpeg,gif,webp,pdf",
    )

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        override: str = config("SQLALCHEMY_DATABASE_URI", cast=str, default="")
        if override:
            return override

        return build_database_uri(self)


settings = Settings()
