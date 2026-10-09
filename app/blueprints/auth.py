from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import limiter
from app.forms.auth import LoginForm, PasswordResetForm, PasswordResetRequestForm, RegisterForm
from app.services.auth import AuthService
from app.services.schemas.auth import (
    AuthLoginError,
    AuthLoginIn,
    AuthPasswordResetIn,
    AuthPasswordResetRequestIn,
    AuthRegisterError,
    AuthRegisterIn,
    AuthValidateResetTokenIn,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        result = AuthService().login(
            AuthLoginIn(email=form.email.data, password=form.password.data, remember_me=form.remember_me.data)
        )

        if result.success:
            login_user(result.user, remember=form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))

        if result.error == AuthLoginError.INACTIVE_ACCOUNT:
            flash(_("This account is disabled."), "danger")
        else:
            flash(_("Invalid email or password."), "danger")

    return render_template("blueprints/auth/login.html", title=_("Log in"), form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        result = AuthService().register(
            AuthRegisterIn(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
            )
        )

        if result.success:
            login_user(result.user)
            flash(_("Welcome! Your account has been created."), "success")
            return redirect(url_for("main.index"))

        if result.error == AuthRegisterError.EMAIL_TAKEN:
            flash(_("An account with this email already exists."), "danger")
        else:
            flash(_("This username is already taken."), "danger")

    return render_template("blueprints/auth/register.html", title=_("Register"), form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/password-reset", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        AuthService().request_password_reset(
            AuthPasswordResetRequestIn(email=form.email.data, ip_address=request.remote_addr)
        )

        flash(_("If that email is registered, a reset link has been sent."), "info")
        return redirect(url_for("auth.login"))

    return render_template("blueprints/auth/password_reset_request.html", title=_("Reset password"), form=form)


@auth_bp.route("/password-reset/<token>", methods=["GET", "POST"])
def password_reset(token: str):
    auth_service = AuthService()

    if not auth_service.validate_reset_token(AuthValidateResetTokenIn(token=token)).valid:
        flash(_("This password reset link is invalid or has expired."), "danger")
        return redirect(url_for("auth.password_reset_request"))

    form = PasswordResetForm()
    if form.validate_on_submit():
        result = auth_service.reset_password(AuthPasswordResetIn(token=token, password=form.password.data))

        if result.success:
            flash(_("Your password has been reset. You can now log in."), "success")
            return redirect(url_for("auth.login"))

        flash(_("This password reset link is invalid or has expired."), "danger")
        return redirect(url_for("auth.password_reset_request"))

    return render_template("blueprints/auth/password_reset.html", title=_("Set new password"), form=form)
