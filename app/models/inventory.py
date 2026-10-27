from app.core.extensions import db
from app.models.mixins import TimestampMixin


class Inventory(TimestampMixin, db.Model):
    __tablename__ = "inventories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, server_default="active")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    user = db.relationship("User", back_populates="inventories", lazy="joined")
