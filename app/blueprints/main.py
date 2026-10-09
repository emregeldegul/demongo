from flask import Blueprint, current_app, redirect, render_template, request, session, url_for
from flask_babel import gettext as _
from sqlalchemy import text

from app.extensions import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/index")
def index():
    title = _("Home")
    description = _("Welcome to the home page.")

    return render_template(
        "blueprints/main/index.html",
        title=title,
        description=description,
    )


@main_bp.route("/set-locale/<locale>")
def set_locale(locale: str):
    if locale in current_app.config["LANGUAGES"]:
        session["locale"] = locale

    return redirect(request.referrer or url_for("main.index"))


@main_bp.route("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 — any failure here means "unhealthy", not a bug to surface
        return {"status": "error"}, 503

    return {"status": "ok"}, 200
