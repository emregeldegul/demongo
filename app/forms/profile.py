from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flask_login import current_user

from app.models.user import User


class EditProfileForm(FlaskForm):
    email = StringField(
        'E-Mail',
        validators=[DataRequired(), Email(), Length(max=70)],
        render_kw={'placeholder': 'E-Mail'}
    )
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=30)],
        render_kw={'placeholder': 'Name', 'autofocus': True}
    )
    note = TextAreaField('Note')
    submit = SubmitField('Save')

    @staticmethod
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user and user != current_user:
            raise ValidationError('This e-mail address cannot be used')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        'Old Password',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Old Password'}
    )
    new_password = PasswordField(
        'New Password',
        validators=[DataRequired(), Length(min=6, max=20)],
        render_kw={'placeholder': 'New Password'}
    )
    password_confirm = PasswordField(
        'New Password Confirm',
        validators=[DataRequired(), EqualTo('new_password')],
        render_kw={'placeholder': 'New Password Confirm'}
    )
    submit = SubmitField('Change Password')

    @staticmethod
    def validate_old_password(self, old_password):
        user = User.query.filter_by(email=current_user.email).first()

        if not user.check_password(old_password.data):
            raise ValidationError('Old password could not be confirmed')
