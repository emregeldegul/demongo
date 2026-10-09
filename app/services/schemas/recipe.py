from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.helpers.costing_helpers import CostingBreakdown
from app.models.recipe import ProductRecipe


class RecipeSaveError(str, Enum):
    NOT_FOUND = "not_found"
    NO_ITEMS = "no_items"
    UNKNOWN_MATERIAL = "unknown_material"


class RecipeDeleteError(str, Enum):
    NOT_FOUND = "not_found"


@dataclass
class RecipeItemIn:
    material_id: int
    quantity: float


@dataclass
class RecipeSaveIn:
    name: str
    labor_hours: float
    hourly_rate: float
    overhead_percentage: float
    tax_percentage: float
    profit_margin_percentage: float
    items: list[RecipeItemIn] = field(default_factory=list)
    # None creates a new recipe; an id updates that one in place.
    recipe_id: int | None = None


@dataclass
class RecipeSaveOut:
    success: bool
    error: RecipeSaveError | None = None
    recipe: ProductRecipe | None = None


@dataclass
class RecipeListIn:
    pass


@dataclass
class RecipeListOut:
    recipes: list[ProductRecipe]


@dataclass
class RecipeGetIn:
    recipe_id: int


@dataclass
class RecipeGetOut:
    success: bool
    recipe: ProductRecipe | None = None
    # Derived from the stored inputs rather than stored in extra columns.
    breakdown: CostingBreakdown | None = None


@dataclass
class RecipeDeleteIn:
    recipe_id: int


@dataclass
class RecipeDeleteOut:
    success: bool
    error: RecipeDeleteError | None = None
