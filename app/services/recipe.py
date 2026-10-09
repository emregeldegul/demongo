from app.extensions import db
from app.helpers.costing_helpers import CostingBreakdown, calculate_costing
from app.models.material import Material
from app.models.recipe import ProductRecipe, RecipeItem
from app.services.schemas.recipe import (
    RecipeDeleteError,
    RecipeDeleteIn,
    RecipeDeleteOut,
    RecipeGetIn,
    RecipeGetOut,
    RecipeListIn,
    RecipeListOut,
    RecipeSaveError,
    RecipeSaveIn,
    RecipeSaveOut,
)


class RecipeService:
    def list(self, data: RecipeListIn) -> RecipeListOut:
        statement = db.select(ProductRecipe).order_by(ProductRecipe.created_at.desc())

        return RecipeListOut(recipes=list(db.session.scalars(statement)))

    def get(self, data: RecipeGetIn) -> RecipeGetOut:
        recipe = db.session.get(ProductRecipe, data.recipe_id)
        if recipe is None:
            return RecipeGetOut(success=False)

        return RecipeGetOut(success=True, recipe=recipe, breakdown=self.breakdown_for(recipe))

    def save(self, data: RecipeSaveIn) -> RecipeSaveOut:
        if not data.items:
            return RecipeSaveOut(success=False, error=RecipeSaveError.NO_ITEMS)

        recipe = ProductRecipe()
        if data.recipe_id is not None:
            recipe = db.session.get(ProductRecipe, data.recipe_id)
            if recipe is None:
                return RecipeSaveOut(success=False, error=RecipeSaveError.NOT_FOUND)

        materials = {
            material.id: material
            for material in db.session.scalars(
                db.select(Material).filter(Material.id.in_({item.material_id for item in data.items}))
            )
        }
        if any(item.material_id not in materials for item in data.items):
            return RecipeSaveOut(success=False, error=RecipeSaveError.UNKNOWN_MATERIAL)

        # Unit costs are read from the database, never from the submitted form:
        # the browser's live preview is a convenience, not an input we trust.
        items = [
            RecipeItem(
                material_id=item.material_id,
                quantity=item.quantity,
                unit_cost_snapshot=materials[item.material_id].unit_cost,
                subtotal_cost=item.quantity * materials[item.material_id].unit_cost,
            )
            for item in data.items
        ]
        breakdown = calculate_costing(
            total_material_cost=sum(item.subtotal_cost for item in items),
            labor_hours=data.labor_hours,
            hourly_rate=data.hourly_rate,
            overhead_percentage=data.overhead_percentage,
            profit_margin_percentage=data.profit_margin_percentage,
            tax_percentage=data.tax_percentage,
        )

        recipe.name = data.name
        recipe.labor_hours = data.labor_hours
        recipe.hourly_rate = data.hourly_rate
        recipe.overhead_percentage = data.overhead_percentage
        recipe.tax_percentage = data.tax_percentage
        recipe.profit_margin_percentage = data.profit_margin_percentage
        recipe.total_material_cost = breakdown.total_material_cost
        recipe.total_cost = breakdown.net_cost
        recipe.suggested_price = breakdown.suggested_price
        # Assigning over the list lets delete-orphan clear the previous lines.
        recipe.items = items

        db.session.add(recipe)
        db.session.commit()

        return RecipeSaveOut(success=True, recipe=recipe)

    def delete(self, data: RecipeDeleteIn) -> RecipeDeleteOut:
        recipe = db.session.get(ProductRecipe, data.recipe_id)
        if recipe is None:
            return RecipeDeleteOut(success=False, error=RecipeDeleteError.NOT_FOUND)

        db.session.delete(recipe)
        db.session.commit()

        return RecipeDeleteOut(success=True)

    def breakdown_for(self, recipe: ProductRecipe) -> CostingBreakdown:
        """Re-derive labor/overhead/tax from what was stored — they aren't columns."""
        return calculate_costing(
            total_material_cost=recipe.total_material_cost,
            labor_hours=recipe.labor_hours,
            hourly_rate=recipe.hourly_rate,
            overhead_percentage=recipe.overhead_percentage,
            profit_margin_percentage=recipe.profit_margin_percentage,
            tax_percentage=recipe.tax_percentage,
        )
