from __future__ import annotations

from sqlalchemy import Boolean, Float, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import MaterialCategory
from app.models._base import BaseModel


class Material(BaseModel):
    """A raw input the workshop buys — priced per `unit` (piece, pack, gram, ...)."""

    __tablename__ = "materials"

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    # values_callable: without it SQLAlchemy would persist the member *names*
    # ("ASSEMBLY_MORTAR"); we want the lowercase values the enum declares.
    category: Mapped[MaterialCategory] = mapped_column(
        SAEnum(MaterialCategory, native_enum=False, length=30, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        index=True,
    )
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Soft-delete: a material used by a saved recipe can't be removed without
    # breaking that recipe's history, so it gets deactivated instead.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
