from typing import Any

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import FieldList, FloatField, Form, FormField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional

from app.models.material import Material


def _optional_int(value: Any) -> int | None:
    # A row the user added but never filled in submits an empty material id.
    # Coercing that to None (instead of letting int("") blow up) lets Optional()
    # clear the error and leaves the row to be dropped server-side.
    try:
        return int(value)
    except TypeError, ValueError:
        return None


class RecipeItemForm(Form):
    """One material line. A plain Form, not a FlaskForm — nested CSRF tokens make no sense."""

    material_id = SelectField(_l("Material"), coerce=_optional_int, validators=[Optional()])
    quantity = FloatField(_l("Quantity"), validators=[Optional(), NumberRange(min=0)])


class RecipeCalculatorForm(FlaskForm):
    name = StringField(_l("Product name / code"), validators=[DataRequired(), Length(max=150)])
    items = FieldList(FormField(RecipeItemForm), min_entries=1)

    labor_hours = FloatField(_l("Labor hours"), validators=[InputRequired(), NumberRange(min=0)], default=0.0)
    hourly_rate = FloatField(_l("Hourly rate"), validators=[InputRequired(), NumberRange(min=0)], default=0.0)
    overhead_percentage = FloatField(
        _l("Overhead (%)"), validators=[InputRequired(), NumberRange(min=0, max=1000)], default=0.0
    )
    profit_margin_percentage = FloatField(
        _l("Profit margin (%)"), validators=[InputRequired(), NumberRange(min=0, max=1000)], default=0.0
    )
    tax_percentage = FloatField(
        _l("Tax / VAT (%)"), validators=[InputRequired(), NumberRange(min=0, max=1000)], default=0.0
    )

    submit = SubmitField(_l("Save recipe"))

    def set_material_choices(self, materials: list[Material]) -> None:
        """Entries exist only after __init__ has read the formdata, so this runs from the route."""
        choices = [("", _l("Select a material..."))] + [
            (str(material.id), f"{material.name} ({material.unit})") for material in materials
        ]
        for entry in self.items:
            entry.material_id.choices = choices
