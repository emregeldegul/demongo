from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import login_required

from app.enums import MaterialCategory
from app.forms.common import ConfirmDeleteForm
from app.forms.material import MaterialForm
from app.services.material import MaterialService
from app.services.schemas.material import (
    MaterialCreateIn,
    MaterialDeleteIn,
    MaterialGetIn,
    MaterialListIn,
    MaterialSaveError,
    MaterialUpdateIn,
)

materials_bp = Blueprint("materials", __name__)


@materials_bp.route("/")
@login_required
def index():
    result = MaterialService().list(MaterialListIn())

    return render_template(
        "blueprints/materials/list.html",
        title=_("Materials"),
        materials=result.materials,
        delete_form=ConfirmDeleteForm(),
    )


@materials_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = MaterialForm()
    if form.validate_on_submit():
        result = MaterialService().create(
            MaterialCreateIn(
                name=form.name.data.strip(),
                category=MaterialCategory(form.category.data),
                unit=form.unit.data.strip(),
                unit_cost=form.unit_cost.data,
                is_active=form.is_active.data,
            )
        )

        if result.success:
            flash(_("Material added."), "success")
            return redirect(url_for("materials.index"))

        flash(_("A material with this name already exists."), "danger")

    return render_template("blueprints/materials/form.html", title=_("New material"), form=form, material=None)


@materials_bp.route("/<int:material_id>/edit", methods=["GET", "POST"])
@login_required
def edit(material_id: int):
    found = MaterialService().get(MaterialGetIn(material_id=material_id))
    if not found.success:
        flash(_("That material no longer exists."), "warning")
        return redirect(url_for("materials.index"))

    form = MaterialForm(obj=found.material)
    if request.method == "GET":
        # obj= puts the enum member in .data, which renders as "MaterialCategory.POT".
        form.category.data = found.material.category.value

    if form.validate_on_submit():
        result = MaterialService().update(
            MaterialUpdateIn(
                material_id=material_id,
                name=form.name.data.strip(),
                category=MaterialCategory(form.category.data),
                unit=form.unit.data.strip(),
                unit_cost=form.unit_cost.data,
                is_active=form.is_active.data,
            )
        )

        if result.success:
            flash(_("Material updated."), "success")
            return redirect(url_for("materials.index"))

        if result.error == MaterialSaveError.NAME_TAKEN:
            flash(_("A material with this name already exists."), "danger")
        else:
            flash(_("That material no longer exists."), "warning")
            return redirect(url_for("materials.index"))

    return render_template(
        "blueprints/materials/form.html", title=_("Edit material"), form=form, material=found.material
    )


@materials_bp.route("/<int:material_id>/delete", methods=["POST"])
@login_required
def delete(material_id: int):
    if not ConfirmDeleteForm().validate_on_submit():
        flash(_("That request could not be verified. Please try again."), "danger")
        return redirect(url_for("materials.index"))

    result = MaterialService().delete(MaterialDeleteIn(material_id=material_id))

    if not result.success:
        flash(_("That material no longer exists."), "warning")
    elif result.deactivated:
        flash(_("This material is used by a saved recipe, so it was deactivated instead of deleted."), "info")
    else:
        flash(_("Material deleted."), "success")

    return redirect(url_for("materials.index"))
