from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.models.user import User


class ProfileUpdateError(str, Enum):
    EMAIL_TAKEN = "email_taken"
    USERNAME_TAKEN = "username_taken"


class ProfileChangePasswordError(str, Enum):
    INVALID_CURRENT_PASSWORD = "invalid_current_password"


@dataclass
class ProfileUpdateIn:
    user_id: int
    email: str
    username: str
    first_name: str | None = None
    last_name: str | None = None


@dataclass
class ProfileUpdateOut:
    success: bool
    error: ProfileUpdateError | None = None
    user: User | None = None


@dataclass
class ProfileChangePasswordIn:
    user_id: int
    current_password: str
    new_password: str


@dataclass
class ProfileChangePasswordOut:
    success: bool
    error: ProfileChangePasswordError | None = None
