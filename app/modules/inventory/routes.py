from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.core.auth.decorators import require_permission
from app.core.exceptions import AppError
from app.modules.inventory.service import InventoryService


inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.get("")
@require_permission("inventory", "list")
def list_inventory():
    search = request.args.get("q", "").strip() or None
    items = InventoryService.list_items(search=search)
    return render_template("inventory/list.html", items=items, search=search or "", users=InventoryService.list_users(), form_data={})


@inventory_bp.post("")
@require_permission("inventory", "list")
def create_inventory():
    try:
        item = InventoryService.create_item(request.form)
    except AppError as error:
        return render_template(
            "inventory/list.html", items=InventoryService.list_items(), search="",
            users=InventoryService.list_users(), error=error.message,
            form_data={"name": request.form.get("name", ""), "status": request.form.get("status", "active"), "user_id": request.form.get("user_id", "")},
        ), error.status_code
    return redirect(url_for("inventory.detail_inventory", item_id=item["id"], created="1"))


@inventory_bp.get("/<int:item_id>")
@require_permission("inventory", "detail")
def detail_inventory(item_id):
    item = InventoryService.get_item(item_id)
    return render_template("inventory/detail.html", item=item, users=InventoryService.list_users())


@inventory_bp.post("/<int:item_id>/user")
@require_permission("inventory", "detail")
def update_inventory_users(item_id):
    try:
        InventoryService.set_item_user(item_id, request.form.get("user_id"))
    except AppError as error:
        item = InventoryService.get_item(item_id)
        return render_template("inventory/detail.html", item=item, users=InventoryService.list_users(), error=error.message), error.status_code
    flash("User terkait berhasil diperbarui.", "success")
    return redirect(url_for("inventory.detail_inventory", item_id=item_id))
