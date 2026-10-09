from flask import Blueprint, flash, redirect, render_template, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app.forms.profile import ProfileChangePasswordForm, ProfileEditForm
from app.services.profile import ProfileService
from app.services.schemas.profile import ProfileChangePasswordIn, ProfileUpdateError, ProfileUpdateIn

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/")
@login_required
def view():
    return render_template("blueprints/profile/view.html", title=_("Profile"))


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    form = ProfileEditForm(obj=current_user)
    if form.validate_on_submit():
        result = ProfileService().update(
            ProfileUpdateIn(
                user_id=current_user.id,
                email=form.email.data,
                username=form.username.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
            )
        )

        if result.success:
            flash(_("Your profile has been updated."), "success")
            return redirect(url_for("profile.view"))

        if result.error == ProfileUpdateError.EMAIL_TAKEN:
            flash(_("An account with this email already exists."), "danger")
        else:
            flash(_("This username is already taken."), "danger")

    return render_template("blueprints/profile/edit.html", title=_("Edit profile"), form=form)


@profile_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ProfileChangePasswordForm()
    if form.validate_on_submit():
        result = ProfileService().change_password(
            ProfileChangePasswordIn(
                user_id=current_user.id,
                current_password=form.current_password.data,
                new_password=form.new_password.data,
            )
        )

        if result.success:
            flash(_("Your password has been changed."), "success")
            return redirect(url_for("profile.view"))

        flash(_("Your current password is incorrect."), "danger")

    return render_template("blueprints/profile/change_password.html", title=_("Change password"), form=form)
