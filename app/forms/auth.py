from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember me"))
    submit = SubmitField(_l("Log in"))


class RegisterForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    username = StringField(_l("Username"), validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField(_l("Password"), validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        _l("Confirm password"),
        validators=[DataRequired(), EqualTo("password", message=_l("Passwords must match."))],
    )
    submit = SubmitField(_l("Register"))


class PasswordResetRequestForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Send reset link"))


class PasswordResetForm(FlaskForm):
    password = PasswordField(_l("New password"), validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        _l("Confirm new password"),
        validators=[DataRequired(), EqualTo("password", message=_l("Passwords must match."))],
    )
    submit = SubmitField(_l("Reset password"))
