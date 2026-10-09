from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import login_required

from app.forms.recipe import RecipeCalculatorForm
from app.models.material import Material
from app.models.recipe import ProductRecipe
from app.services.material import MaterialService
from app.services.recipe import RecipeService
from app.services.schemas.material import MaterialListIn
from app.services.schemas.recipe import RecipeGetIn, RecipeItemIn, RecipeSaveError, RecipeSaveIn

calculator_bp = Blueprint("calculator", __name__)


@calculator_bp.route("/", methods=["GET", "POST"])
@calculator_bp.route("/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def index(recipe_id: int | None = None):
    recipe_service = RecipeService()

    recipe = None
    if recipe_id is not None:
        found = recipe_service.get(RecipeGetIn(recipe_id=recipe_id))
        if not found.success:
            flash(_("That recipe no longer exists."), "warning")
            return redirect(url_for("recipes.index"))
        recipe = found.recipe

    materials = _selectable_materials(recipe)

    form = RecipeCalculatorForm(data=_form_data(recipe) if request.method == "GET" else None)
    form.set_material_choices(materials)

    if form.validate_on_submit():
        result = recipe_service.save(
            RecipeSaveIn(
                recipe_id=recipe_id,
                name=form.name.data.strip(),
                labor_hours=form.labor_hours.data,
                hourly_rate=form.hourly_rate.data,
                overhead_percentage=form.overhead_percentage.data,
                profit_margin_percentage=form.profit_margin_percentage.data,
                tax_percentage=form.tax_percentage.data,
                items=[
                    RecipeItemIn(material_id=entry.material_id.data, quantity=entry.quantity.data)
                    for entry in form.items
                    if entry.material_id.data and entry.quantity.data
                ],
            )
        )

        if result.success:
            flash(_("Recipe saved."), "success")
            return redirect(url_for("recipes.detail", recipe_id=result.recipe.id))

        if result.error == RecipeSaveError.NO_ITEMS:
            flash(_("Add at least one material line with a quantity."), "danger")
        elif result.error == RecipeSaveError.UNKNOWN_MATERIAL:
            flash(_("One of the selected materials no longer exists."), "danger")
        else:
            flash(_("That recipe no longer exists."), "warning")
            return redirect(url_for("recipes.index"))

    return render_template(
        "blueprints/calculator/index.html",
        title=_("Edit recipe") if recipe else _("Cost calculator"),
        form=form,
        recipe=recipe,
        # Unit costs the live preview multiplies by; the server re-reads them on save.
        material_costs={str(material.id): material.unit_cost for material in materials},
    )


def _selectable_materials(recipe: ProductRecipe | None) -> list[Material]:
    materials = MaterialService().list(MaterialListIn(include_inactive=False)).materials
    if recipe is None:
        return materials

    # A deactivated material still used by this recipe has to stay in the
    # dropdown, otherwise reopening the recipe would silently drop that line.
    known = {material.id for material in materials}
    extra = [item.material for item in recipe.items if item.material_id not in known]

    return sorted(materials + extra, key=lambda material: material.name)


def _form_data(recipe: ProductRecipe | None) -> dict | None:
    if recipe is None:
        return None

    return {
        "name": recipe.name,
        "labor_hours": recipe.labor_hours,
        "hourly_rate": recipe.hourly_rate,
        "overhead_percentage": recipe.overhead_percentage,
        "profit_margin_percentage": recipe.profit_margin_percentage,
        "tax_percentage": recipe.tax_percentage,
        "items": [{"material_id": item.material_id, "quantity": item.quantity} for item in recipe.items],
    }
