from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user

from app.models.user import User
from app.forms.profile import EditProfileForm, ChangePasswordForm

profile = Blueprint('profile', __name__, url_prefix='/profile')


@profile.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = EditProfileForm()

    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()

        user.name = form.name.data
        user.email = form.email.data
        user.note = form.note.data
        user.save()

        flash('Profile Successfully Updated', 'success')

    form.name.data = current_user.name
    form.email.data = current_user.email
    form.note.data = current_user.note

    return render_template('views/profile/index.html', title='Edit Profile', form=form)


@profile.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()

        user.generate_password_hash(form.new_password.data)
        user.save()

        flash('Password Successfully Updated', 'success')


    return render_template('views/profile/password.html', title='Edit Password', form=form)