# Architecture

This Flask monolith uses:

- `app/__init__.py` for the application factory
- `app/core/` for extensions, auth, errors, and shared infrastructure
- `app/models/` for SQLAlchemy models
- `app/modules/` for feature modules
- `app/templates/` for Jinja templates
- `app/static/` for frontend assets

Current example module:

- `inventory`: Inventory list, create, and detail flow
