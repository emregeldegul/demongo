from __future__ import annotations

import datetime
import hashlib
import secrets

from flask_login import UserMixin
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager
from app.helpers.time_helpers import utcnow
from app.models._base import BaseModel

PASSWORD_RESET_TOKEN_TTL = datetime.timedelta(hours=1)


class User(UserMixin, BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    first_name: Mapped[str | None] = mapped_column(String(150))
    last_name: Mapped[str | None] = mapped_column(String(150))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    last_login_at: Mapped[datetime.datetime | None] = mapped_column(DateTime)

    password_reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    registration_history: Mapped[list[UserRegistrationHistory]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class PasswordResetToken(BaseModel):
    """One row per requested reset link — kept after use as an audit history."""

    __tablename__ = "password_reset_tokens"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    requested_ip: Mapped[str | None] = mapped_column(String(45))

    user: Mapped[User] = relationship(back_populates="password_reset_tokens")

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @classmethod
    def issue(
        cls,
        user: User,
        *,
        ttl: datetime.timedelta = PASSWORD_RESET_TOKEN_TTL,
        requested_ip: str | None = None,
    ) -> tuple[PasswordResetToken, str]:
        raw_token = secrets.token_urlsafe(32)
        token = cls(
            user=user,
            token_hash=cls.hash_token(raw_token),
            expires_at=utcnow() + ttl,
            requested_ip=requested_ip,
        )
        return token, raw_token

    @property
    def is_expired(self) -> bool:
        return utcnow() >= self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None


class UserRegistrationHistory(BaseModel):
    """One row per registration event, for audit purposes."""

    __tablename__ = "user_registration_history"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    registered_ip: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(255))

    user: Mapped[User] = relationship(back_populates="registration_history")


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))
