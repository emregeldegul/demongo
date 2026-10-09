from flask import Blueprint, flash, redirect, render_template, url_for
from flask_babel import gettext as _
from flask_login import login_required

from app.forms.common import ConfirmDeleteForm
from app.services.recipe import RecipeService
from app.services.schemas.recipe import RecipeDeleteIn, RecipeGetIn, RecipeListIn

recipes_bp = Blueprint("recipes", __name__)


@recipes_bp.route("/")
@login_required
def index():
    result = RecipeService().list(RecipeListIn())

    return render_template(
        "blueprints/recipes/list.html",
        title=_("Recipes"),
        recipes=result.recipes,
        delete_form=ConfirmDeleteForm(),
    )


@recipes_bp.route("/<int:recipe_id>")
@login_required
def detail(recipe_id: int):
    result = RecipeService().get(RecipeGetIn(recipe_id=recipe_id))
    if not result.success:
        flash(_("That recipe no longer exists."), "warning")
        return redirect(url_for("recipes.index"))

    return render_template(
        "blueprints/recipes/detail.html",
        title=result.recipe.name,
        recipe=result.recipe,
        breakdown=result.breakdown,
        delete_form=ConfirmDeleteForm(),
    )


@recipes_bp.route("/<int:recipe_id>/delete", methods=["POST"])
@login_required
def delete(recipe_id: int):
    if not ConfirmDeleteForm().validate_on_submit():
        flash(_("That request could not be verified. Please try again."), "danger")
        return redirect(url_for("recipes.index"))

    result = RecipeService().delete(RecipeDeleteIn(recipe_id=recipe_id))
    if result.success:
        flash(_("Recipe deleted."), "success")
    else:
        flash(_("That recipe no longer exists."), "warning")

    return redirect(url_for("recipes.index"))
