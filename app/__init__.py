from os import getenv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    """
        A common pattern is creating the application object when the blueprint
        is imported. But if you move the creation of this object into a
        function, you can then create multiple instances of this app later.

        Application Factories:
            https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    @app.context_processor
    def context_processor():
        return dict(
            site_url = getenv('SITE_URL'),
            site_name = getenv('SITE_NAME'),
        )

    # Routes
    """
        Each route file acts like an application.
        So it will be easier to add new applications and fix existing
        applications.
    """
    from app.routes.auth import auth
    app.register_blueprint(auth)

    from app.routes.main import main
    app.register_blueprint(main)

    return app
