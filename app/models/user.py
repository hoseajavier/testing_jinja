from app.core.extensions import db
from app.models.mixins import TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    role = db.Column(db.String(30), nullable=False, default="user", server_default="user")
    inventories = db.relationship("Inventory", back_populates="user", lazy="selectin")
