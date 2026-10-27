from app.core.extensions import db
from app.models.user import User


class UserRepository:
    @staticmethod
    def list(search=None):
        query = User.query
        if search:
            term = f"%{search.strip()}%"
            query = query.filter(db.or_(User.name.ilike(term), User.email.ilike(term)))
        return query.order_by(User.name.asc(), User.id.asc()).all()

    @staticmethod
    def get_by_id(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email):
        return User.query.filter(db.func.lower(User.email) == email.lower()).first()

    @staticmethod
    def create(user_data):
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user, user_data):
        for key, value in user_data.items():
            setattr(user, key, value)
        db.session.commit()
        return user

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()
