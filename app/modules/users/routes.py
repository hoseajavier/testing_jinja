from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.core.exceptions import AppError
from app.modules.users.service import UserService


users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.get("")
def list_users():
    search = request.args.get("q", "").strip() or None
    users = UserService.list_users(search=search)
    return render_template("users/list.html", users=users, search=search or "")


@users_bp.route("/new", methods=["GET", "POST"])
def create_user():
    if request.method == "GET":
        return render_template("users/form.html", user=None, form_data={}, page_title="Tambah User")
    try:
        user = UserService.create_user(request.form)
    except AppError as error:
        return render_template(
            "users/form.html", user=None, form_data=request.form, page_title="Tambah User", error=error.message
        ), error.status_code
    flash("User berhasil ditambahkan.", "success")
    return redirect(url_for("users.list_users"))


@users_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    user = UserService.get_user(user_id)
    if request.method == "GET":
        return render_template("users/form.html", user=user, form_data=user, page_title="Edit User")
    try:
        UserService.update_user(user_id, request.form)
    except AppError as error:
        return render_template(
            "users/form.html", user=user, form_data={**user, **request.form}, page_title="Edit User", error=error.message
        ), error.status_code
    flash("Perubahan user berhasil disimpan.", "success")
    return redirect(url_for("users.list_users"))


@users_bp.post("/<int:user_id>/delete")
def delete_user(user_id):
    UserService.delete_user(user_id)
    flash("User berhasil dihapus.", "success")
    return redirect(url_for("users.list_users"))
