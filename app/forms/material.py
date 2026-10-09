from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, FloatField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange

from app.enums import MaterialCategory


class MaterialForm(FlaskForm):
    name = StringField(_l("Name"), validators=[DataRequired(), Length(max=150)])
    # Plain values, not the members themselves: str(MaterialCategory.POT) renders
    # as "MaterialCategory.POT", so the route converts the value back instead.
    category = SelectField(
        _l("Category"),
        validators=[DataRequired()],
        choices=[(category.value, category.label) for category in MaterialCategory],
    )
    unit = StringField(_l("Unit"), validators=[DataRequired(), Length(max=30)], description=_l("e.g. piece, pack, g"))
    unit_cost = FloatField(_l("Unit cost"), validators=[InputRequired(), NumberRange(min=0)])
    is_active = BooleanField(_l("Active"), default=True)
    submit = SubmitField(_l("Save material"))
