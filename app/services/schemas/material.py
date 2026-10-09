from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.enums import MaterialCategory
from app.models.material import Material


class MaterialSaveError(str, Enum):
    NOT_FOUND = "not_found"
    NAME_TAKEN = "name_taken"


class MaterialDeleteError(str, Enum):
    NOT_FOUND = "not_found"


@dataclass
class MaterialListIn:
    include_inactive: bool = True


@dataclass
class MaterialListOut:
    materials: list[Material]


@dataclass
class MaterialGetIn:
    material_id: int


@dataclass
class MaterialGetOut:
    success: bool
    material: Material | None = None


@dataclass
class MaterialCreateIn:
    name: str
    category: MaterialCategory
    unit: str
    unit_cost: float
    is_active: bool = True


@dataclass
class MaterialCreateOut:
    success: bool
    error: MaterialSaveError | None = None
    material: Material | None = None


@dataclass
class MaterialUpdateIn:
    material_id: int
    name: str
    category: MaterialCategory
    unit: str
    unit_cost: float
    is_active: bool = True


@dataclass
class MaterialUpdateOut:
    success: bool
    error: MaterialSaveError | None = None
    material: Material | None = None


@dataclass
class MaterialDeleteIn:
    material_id: int


@dataclass
class MaterialDeleteOut:
    success: bool
    error: MaterialDeleteError | None = None
    # True when the material was referenced by a saved recipe and therefore
    # deactivated instead of removed — the caller words the message differently.
    deactivated: bool = False
