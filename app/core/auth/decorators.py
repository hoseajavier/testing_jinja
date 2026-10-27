from functools import wraps


def require_permission(_page_key, _sub_page_key=None):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            return view(*args, **kwargs)

        return wrapped

    return decorator
