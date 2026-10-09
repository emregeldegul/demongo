from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class ProfileEditForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    username = StringField(_l("Username"), validators=[DataRequired(), Length(min=3, max=150)])
    first_name = StringField(_l("First name"), validators=[Optional(), Length(max=150)])
    last_name = StringField(_l("Last name"), validators=[Optional(), Length(max=150)])
    submit = SubmitField(_l("Save changes"))


class ProfileChangePasswordForm(FlaskForm):
    current_password = PasswordField(_l("Current password"), validators=[DataRequired()])
    new_password = PasswordField(_l("New password"), validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        _l("Confirm new password"),
        validators=[DataRequired(), EqualTo("new_password", message=_l("Passwords must match."))],
    )
    submit = SubmitField(_l("Change password"))
