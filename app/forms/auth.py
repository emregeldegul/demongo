from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo

from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()],
        render_kw={'placeholder': 'E-Mail'})
    password = PasswordField('Password', validators=[DataRequired()],
        render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()],
        render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name', validators=[DataRequired()],
        render_kw={'placeholder': 'Last Name'})
    email = StringField('E-Mail', validators=[DataRequired(), Email()],
        render_kw={'placeholder': 'E-Mail'})
    password = PasswordField('Password', validators=[DataRequired()],
        render_kw={'placeholder': 'Password'})
    password_confirm = PasswordField( 'Password Confirm',
        validators=[DataRequired(), EqualTo('password')],
        render_kw={'placeholder': 'Password Confirm'})
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('User is available.')
