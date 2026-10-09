from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField


class ConfirmDeleteForm(FlaskForm):
    """Fields-free on purpose: it exists so destructive POSTs carry a CSRF token."""

    submit = SubmitField(_l("Delete"))
