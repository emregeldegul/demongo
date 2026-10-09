from flask import current_app, render_template

from app.extensions import db
from app.helpers.mail_helper import send_mail
from app.helpers.time_helpers import utcnow
from app.models.user import PASSWORD_RESET_TOKEN_TTL, PasswordResetToken, User, UserRegistrationHistory
from app.services.schemas.auth import (
    AuthLoginError,
    AuthLoginIn,
    AuthLoginOut,
    AuthPasswordResetError,
    AuthPasswordResetIn,
    AuthPasswordResetOut,
    AuthPasswordResetRequestIn,
    AuthPasswordResetRequestOut,
    AuthRegisterError,
    AuthRegisterIn,
    AuthRegisterOut,
    AuthValidateResetTokenIn,
    AuthValidateResetTokenOut,
)


class AuthService:
    def login(self, data: AuthLoginIn) -> AuthLoginOut:
        user = db.session.scalar(db.select(User).filter_by(email=data.email.lower()))

        if user is None or not user.check_password(data.password):
            return AuthLoginOut(success=False, error=AuthLoginError.INVALID_CREDENTIALS)

        if not user.is_active:
            return AuthLoginOut(success=False, error=AuthLoginError.INACTIVE_ACCOUNT)

        user.last_login_at = utcnow()
        db.session.commit()

        return AuthLoginOut(success=True, user=user)

    def register(self, data: AuthRegisterIn) -> AuthRegisterOut:
        email = data.email.lower()

        if db.session.scalar(db.select(User).filter_by(email=email)):
            return AuthRegisterOut(success=False, error=AuthRegisterError.EMAIL_TAKEN)

        if db.session.scalar(db.select(User).filter_by(username=data.username)):
            return AuthRegisterOut(success=False, error=AuthRegisterError.USERNAME_TAKEN)

        user = User(email=email, username=data.username)
        user.set_password(data.password)
        db.session.add(user)
        db.session.flush()

        db.session.add(
            UserRegistrationHistory(
                user_id=user.id,
                registered_ip=data.ip_address,
                user_agent=data.user_agent,
            )
        )
        db.session.commit()

        return AuthRegisterOut(success=True, user=user)

    def request_password_reset(self, data: AuthPasswordResetRequestIn) -> AuthPasswordResetRequestOut:
        user = db.session.scalar(db.select(User).filter_by(email=data.email.lower()))

        if user is None:
            return AuthPasswordResetRequestOut(issued=False)

        token, raw_token = PasswordResetToken.issue(user, requested_ip=data.ip_address)
        db.session.add(token)
        db.session.commit()

        self._send_password_reset_email(user, raw_token)

        return AuthPasswordResetRequestOut(issued=True, user=user, raw_token=raw_token)

    def validate_reset_token(self, data: AuthValidateResetTokenIn) -> AuthValidateResetTokenOut:
        reset_token = self._get_reset_token(data.token)
        valid = reset_token is not None and not reset_token.is_used and not reset_token.is_expired

        return AuthValidateResetTokenOut(valid=valid)

    def reset_password(self, data: AuthPasswordResetIn) -> AuthPasswordResetOut:
        reset_token = self._get_reset_token(data.token)

        if reset_token is None or reset_token.is_used or reset_token.is_expired:
            return AuthPasswordResetOut(success=False, error=AuthPasswordResetError.INVALID_TOKEN)

        reset_token.user.set_password(data.password)
        reset_token.used_at = utcnow()
        db.session.commit()

        return AuthPasswordResetOut(success=True)

    def _send_password_reset_email(self, user: User, raw_token: str) -> None:
        # Built from SITE_URL rather than url_for(..., _external=True): the latter
        # needs an active request (or SERVER_NAME configured), but this service must
        # also work from a shell/background job. Keep this path in sync with the
        # "/password-reset/<token>" route in app/blueprints/auth.py (registered under
        # the "/auth" prefix in app/blueprints/__init__.py).
        site_url = current_app.config["SITE_URL"].rstrip("/")
        reset_url = f"{site_url}/auth/password-reset/{raw_token}"
        hours = int(PASSWORD_RESET_TOKEN_TTL.total_seconds() // 3600)
        context = {
            "user": user,
            "reset_url": reset_url,
            "site_name": current_app.config.get("SITE_NAME", "Demongo"),
            "expires_in": f"{hours} hour" + ("s" if hours != 1 else ""),
        }

        send_mail(
            to=user.email,
            subject="Reset your password",
            text_body=render_template("emails/password_reset.txt", **context),
            html_body=render_template("emails/password_reset.html", **context),
        )

    @staticmethod
    def _get_reset_token(raw_token: str) -> PasswordResetToken | None:
        token_hash = PasswordResetToken.hash_token(raw_token)
        return db.session.scalar(db.select(PasswordResetToken).filter_by(token_hash=token_hash))
