from flask import jsonify, render_template, request

from app.core.exceptions import AppError


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": error.message}), error.status_code

        return render_template("errors/error.html", message=error.message), error.status_code
