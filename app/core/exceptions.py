class AppError(Exception):
    status_code = 400

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class ValidationError(AppError):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404
