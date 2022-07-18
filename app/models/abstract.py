from datetime import datetime, date

from app import db


class DictMixin:
    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            
            if not isinstance(
                getattr(self, column.name), (datetime, date)
            )
            else getattr(self, column.name).isoformat()
            
            for column in self.__table__.columns
        }


class BaseModel(db.Model, DictMixin):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now(), server_default=db.func.now(), onupdate=db.func.now())  # noqa

    def save(self):
        if self.id is None:
            db.session.add(self)
        return db.session.commit()

    def destroy(self):
        db.session.delete(self)
        return db.session.commit()
