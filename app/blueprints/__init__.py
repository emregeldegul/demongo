from flask import Flask

from app.blueprints.auth import auth_bp
from app.blueprints.calculator import calculator_bp
from app.blueprints.main import main_bp
from app.blueprints.materials import materials_bp
from app.blueprints.profile import profile_bp
from app.blueprints.recipes import recipes_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(materials_bp, url_prefix="/materials")
    app.register_blueprint(calculator_bp, url_prefix="/calculator")
    app.register_blueprint(recipes_bp, url_prefix="/recipes")
