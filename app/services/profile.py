from app.extensions import db
from app.models.user import User
from app.services.schemas.profile import (
    ProfileChangePasswordError,
    ProfileChangePasswordIn,
    ProfileChangePasswordOut,
    ProfileUpdateError,
    ProfileUpdateIn,
    ProfileUpdateOut,
)


class ProfileService:
    def update(self, data: ProfileUpdateIn) -> ProfileUpdateOut:
        user = db.session.get(User, data.user_id)
        email = data.email.lower()

        if db.session.scalar(db.select(User).filter_by(email=email).filter(User.id != data.user_id)):
            return ProfileUpdateOut(success=False, error=ProfileUpdateError.EMAIL_TAKEN)

        if db.session.scalar(db.select(User).filter_by(username=data.username).filter(User.id != data.user_id)):
            return ProfileUpdateOut(success=False, error=ProfileUpdateError.USERNAME_TAKEN)

        user.email = email
        user.username = data.username
        user.first_name = data.first_name
        user.last_name = data.last_name
        db.session.commit()

        return ProfileUpdateOut(success=True, user=user)

    def change_password(self, data: ProfileChangePasswordIn) -> ProfileChangePasswordOut:
        user = db.session.get(User, data.user_id)

        if not user.check_password(data.current_password):
            return ProfileChangePasswordOut(success=False, error=ProfileChangePasswordError.INVALID_CURRENT_PASSWORD)

        user.set_password(data.new_password)
        db.session.commit()

        return ProfileChangePasswordOut(success=True)
