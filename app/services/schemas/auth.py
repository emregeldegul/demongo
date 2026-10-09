from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.models.user import User


class AuthLoginError(str, Enum):
    INVALID_CREDENTIALS = "invalid_credentials"
    INACTIVE_ACCOUNT = "inactive_account"


class AuthRegisterError(str, Enum):
    EMAIL_TAKEN = "email_taken"
    USERNAME_TAKEN = "username_taken"


class AuthPasswordResetError(str, Enum):
    INVALID_TOKEN = "invalid_token"


@dataclass
class AuthLoginIn:
    email: str
    password: str
    remember_me: bool = False


@dataclass
class AuthLoginOut:
    success: bool
    error: AuthLoginError | None = None
    user: User | None = None


@dataclass
class AuthRegisterIn:
    email: str
    username: str
    password: str
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass
class AuthRegisterOut:
    success: bool
    error: AuthRegisterError | None = None
    user: User | None = None


@dataclass
class AuthPasswordResetRequestIn:
    email: str
    ip_address: str | None = None


@dataclass
class AuthPasswordResetRequestOut:
    issued: bool
    user: User | None = None
    raw_token: str | None = None


@dataclass
class AuthValidateResetTokenIn:
    token: str


@dataclass
class AuthValidateResetTokenOut:
    valid: bool


@dataclass
class AuthPasswordResetIn:
    token: str
    password: str


@dataclass
class AuthPasswordResetOut:
    success: bool
    error: AuthPasswordResetError | None = None
