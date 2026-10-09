from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models._base import BaseModel
from app.models.material import Material


class ProductRecipe(BaseModel):
    """A saved costing: the inputs the user entered plus the totals they produced."""

    __tablename__ = "product_recipes"

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)

    labor_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hourly_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overhead_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tax_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    profit_margin_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Computed server-side on save (never taken from the browser) and frozen here
    # so the recipe keeps showing what it cost on the day it was priced.
    total_material_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    suggested_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    items: Mapped[list[RecipeItem]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", lazy="selectin"
    )


class RecipeItem(BaseModel):
    """One material line of a recipe, with the unit cost it was priced at."""

    __tablename__ = "recipe_items"

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("product_recipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), nullable=False, index=True)

    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Snapshot, not a live lookup: repricing a material must not silently rewrite
    # the totals of every recipe already saved with it.
    unit_cost_snapshot: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    subtotal_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    recipe: Mapped[ProductRecipe] = relationship(back_populates="items")
    material: Mapped[Material] = relationship(lazy="joined")
