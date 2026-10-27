from app.core.extensions import db
from app.models.inventory import Inventory
from app.models.user import User


class InventoryRepository:
    @staticmethod
    def get_by_id(item_id):
        return Inventory.query.get(item_id)

    @staticmethod
    def list(search=None):
        query = Inventory.query

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(Inventory.name.ilike(term))

        return query.order_by(Inventory.name.asc()).all()

    @staticmethod
    def create(item_data):
        item = Inventory(**item_data)
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def list_users():
        return User.query.order_by(User.name.asc()).all()

    @staticmethod
    def set_user(item, user_id):
        item.user = User.query.filter_by(id=user_id).first() if user_id else None
        db.session.commit()
        return item
