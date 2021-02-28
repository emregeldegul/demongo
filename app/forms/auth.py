from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length

from app.models.user import User


class LoginForm(FlaskForm):
    email = StringField(
        'E-Mail',
        validators=[DataRequired(), Email()],
        render_kw={'placeholder': 'E-Mail', 'autofocus': True},
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Password'}
    )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=30)],
        render_kw={'placeholder': 'Name', 'autofocus': True}
    )
    email = StringField(
        'E-Mail',
        validators=[DataRequired(), Email(), Length(max=70)],
        render_kw={'placeholder': 'E-Mail'}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=20)],
        render_kw={'placeholder': 'Password'}
    )
    password_confirm = PasswordField(
        'Password Confirm',
        validators=[DataRequired(), EqualTo('password')],
        render_kw={'placeholder': 'Password Confirm'}
    )
    submit = SubmitField('Register')

    @staticmethod
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('This e-mail address cannot be used.')
