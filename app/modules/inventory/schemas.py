def item_summary(item):
    return {
        "id": item.id,
        "name": item.name,
        "status": item.status,
        "user": {"id": item.user.id, "name": item.user.name, "email": item.user.email},
        "user_id": item.user_id,
    }


def item_detail(item):
    return {
        **item_summary(item),
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }
