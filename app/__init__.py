from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from settings import settings

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()


def unauthorized(e):
    render_template("assets/403.html"), 403


def page_not_found(e):
    return render_template('assets/404.html'), 404


def international_server_error(e):
    return render_template('assets/500.html'), 500


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please Login To Access This Page'
    login_manager.login_message_category = 'info'

    app.register_error_handler(403, unauthorized)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, international_server_error)

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.auth import auth
    app.register_blueprint(auth)

    from app.routes.profile import profile
    app.register_blueprint(profile)

    return app
