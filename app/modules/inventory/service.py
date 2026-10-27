from app.core.exceptions import NotFoundError, ValidationError
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import item_detail, item_summary


ITEM_STATUSES = {"active", "inactive"}


class InventoryService:
    @staticmethod
    def list_items(search=None):
        items = InventoryRepository.list(search=search)
        return [item_summary(item) for item in items]

    @staticmethod
    def get_item(item_id):
        item = InventoryRepository.get_by_id(item_id)
        if not item:
            raise NotFoundError("Inventory item not found")

        return item_detail(item)

    @staticmethod
    def create_item(form_data):
        name = (form_data.get("name") or "").strip()
        status = (form_data.get("status") or "active").strip()

        if not name:
            raise ValidationError("Name is required")
        if status not in ITEM_STATUSES:
            raise ValidationError("Status is not valid")

        raw_user_id = form_data.get("user_id")
        user_id = InventoryService._parse_user_id(raw_user_id)
        valid_user_ids = {user.id for user in InventoryRepository.list_users()}
        if user_id not in valid_user_ids:
            raise ValidationError("Pilih user yang valid")
        item = InventoryRepository.create({"name": name, "status": status, "user_id": user_id})
        return item_detail(item)

    @staticmethod
    def set_item_user(item_id, raw_user_id):
        item = InventoryRepository.get_by_id(item_id)
        if item is None:
            raise NotFoundError("Inventory item not found")
        user_id = InventoryService._parse_user_id(raw_user_id)
        valid_user_ids = {user.id for user in InventoryRepository.list_users()}
        if user_id not in valid_user_ids:
            raise ValidationError("Pilih user yang valid")
        return item_detail(InventoryRepository.set_user(item, user_id))

    @staticmethod
    def list_users():
        return [{"id": user.id, "name": user.name, "email": user.email} for user in InventoryRepository.list_users()]

    @staticmethod
    def _parse_user_id(raw_user_id):
        try:
            return int(raw_user_id)
        except (TypeError, ValueError) as error:
            raise ValidationError("Pilih user yang valid") from error
