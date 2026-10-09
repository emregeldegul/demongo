from app.extensions import db
from app.models.material import Material
from app.models.recipe import RecipeItem
from app.services.schemas.material import (
    MaterialCreateIn,
    MaterialCreateOut,
    MaterialDeleteError,
    MaterialDeleteIn,
    MaterialDeleteOut,
    MaterialGetIn,
    MaterialGetOut,
    MaterialListIn,
    MaterialListOut,
    MaterialSaveError,
    MaterialUpdateIn,
    MaterialUpdateOut,
)


class MaterialService:
    def list(self, data: MaterialListIn) -> MaterialListOut:
        statement = db.select(Material).order_by(Material.category, Material.name)
        if not data.include_inactive:
            statement = statement.filter_by(is_active=True)

        return MaterialListOut(materials=list(db.session.scalars(statement)))

    def get(self, data: MaterialGetIn) -> MaterialGetOut:
        material = db.session.get(Material, data.material_id)
        if material is None:
            return MaterialGetOut(success=False)

        return MaterialGetOut(success=True, material=material)

    def create(self, data: MaterialCreateIn) -> MaterialCreateOut:
        if self._name_taken(data.name):
            return MaterialCreateOut(success=False, error=MaterialSaveError.NAME_TAKEN)

        material = Material(
            name=data.name,
            category=data.category,
            unit=data.unit,
            unit_cost=data.unit_cost,
            is_active=data.is_active,
        )
        db.session.add(material)
        db.session.commit()

        return MaterialCreateOut(success=True, material=material)

    def update(self, data: MaterialUpdateIn) -> MaterialUpdateOut:
        material = db.session.get(Material, data.material_id)
        if material is None:
            return MaterialUpdateOut(success=False, error=MaterialSaveError.NOT_FOUND)

        if self._name_taken(data.name, exclude_id=material.id):
            return MaterialUpdateOut(success=False, error=MaterialSaveError.NAME_TAKEN)

        material.name = data.name
        material.category = data.category
        material.unit = data.unit
        material.unit_cost = data.unit_cost
        material.is_active = data.is_active
        db.session.commit()

        return MaterialUpdateOut(success=True, material=material)

    def delete(self, data: MaterialDeleteIn) -> MaterialDeleteOut:
        material = db.session.get(Material, data.material_id)
        if material is None:
            return MaterialDeleteOut(success=False, error=MaterialDeleteError.NOT_FOUND)

        # A saved recipe still points here, so removing the row would either
        # break the foreign key or orphan that recipe's line. Deactivate
        # instead: it disappears from the picker, history stays intact.
        if db.session.scalar(db.select(RecipeItem.id).filter_by(material_id=material.id).limit(1)):
            material.is_active = False
            db.session.commit()
            return MaterialDeleteOut(success=True, deactivated=True)

        db.session.delete(material)
        db.session.commit()

        return MaterialDeleteOut(success=True)

    def _name_taken(self, name: str, *, exclude_id: int | None = None) -> bool:
        statement = db.select(Material.id).filter(db.func.lower(Material.name) == name.strip().lower())
        if exclude_id is not None:
            statement = statement.filter(Material.id != exclude_id)

        return db.session.scalar(statement.limit(1)) is not None
