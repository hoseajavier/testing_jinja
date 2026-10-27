def user_summary(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


def user_detail(user):
    return {
        **user_summary(user),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
