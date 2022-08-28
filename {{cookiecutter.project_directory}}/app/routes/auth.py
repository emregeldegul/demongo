from flask import Blueprint, redirect, url_for, render_template, flash
from flask_login import current_user, login_user, logout_user

from app.models.user import User
from app.forms.auth import LoginForm, RegisterForm

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/")
@auth.route("/index")
def index():
    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("main.index"))
        else:
            flash("Login Failed", "danger")

    return render_template("views/auth/login.html", title="Login", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User()
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.generate_password_hash(form.password.data)
        user.save()

        login_user(user)

        return redirect(url_for("main.index"))

    return render_template("views/auth/register.html", title="Register", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    flash("Logged Out", "success")
    return redirect(url_for("auth.login"))
