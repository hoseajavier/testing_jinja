from importlib import import_module

from flask import Flask

from app.config import Config
from app.core.extensions import cors, db, migrate
from app.core.responses import register_error_handlers


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    import_module("app.models")

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])

    register_error_handlers(app)
    register_blueprints(app)

    return app


def register_blueprints(app):
    from app.modules.dashboard.routes import dashboard_bp
    from app.modules.inventory.routes import inventory_bp
    from app.modules.users.routes import users_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(users_bp)
