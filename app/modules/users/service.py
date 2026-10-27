from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import user_detail, user_summary


USER_ROLES = {"admin", "user"}


class UserService:
    @staticmethod
    def list_users(search=None):
        return [user_summary(user) for user in UserRepository.list(search=search)]

    @staticmethod
    def get_user(user_id):
        user = UserRepository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User tidak ditemukan")
        return user_detail(user)

    @staticmethod
    def create_user(form_data):
        data = UserService._validate(form_data)
        if UserRepository.get_by_email(data["email"]):
            raise ValidationError("Email sudah digunakan")
        try:
            return user_detail(UserRepository.create(data))
        except IntegrityError as error:
            from app.core.extensions import db

            db.session.rollback()
            raise ValidationError("Email sudah digunakan") from error

    @staticmethod
    def update_user(user_id, form_data):
        user = UserRepository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User tidak ditemukan")
        data = UserService._validate(form_data)
        duplicate = UserRepository.get_by_email(data["email"])
        if duplicate and duplicate.id != user.id:
            raise ValidationError("Email sudah digunakan")
        try:
            return user_detail(UserRepository.update(user, data))
        except IntegrityError as error:
            from app.core.extensions import db

            db.session.rollback()
            raise ValidationError("Email sudah digunakan") from error

    @staticmethod
    def delete_user(user_id):
        user = UserRepository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User tidak ditemukan")
        UserRepository.delete(user)

    @staticmethod
    def _validate(form_data):
        name = (form_data.get("name") or "").strip()
        email = (form_data.get("email") or "").strip().lower()
        role = (form_data.get("role") or "user").strip().lower()

        if not name:
            raise ValidationError("Nama wajib diisi")
        if len(name) > 120:
            raise ValidationError("Nama maksimal 120 karakter")
        if not email or len(email) > 255 or email.count("@") != 1:
            raise ValidationError("Alamat email tidak valid")
        local, domain = email.split("@")
        if not local or not domain or "." not in domain or any(char.isspace() for char in email):
            raise ValidationError("Alamat email tidak valid")
        if role not in USER_ROLES:
            raise ValidationError("Peran user tidak valid")
        return {"name": name, "email": email, "role": role}
