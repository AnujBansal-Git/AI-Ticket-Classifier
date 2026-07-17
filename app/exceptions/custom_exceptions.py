class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DatasetValidationError(AppException):
    pass


class TrainingError(AppException):
    pass


class PredictionError(AppException):
    pass


class ModelNotFoundError(AppException):
    pass


class CSVError(AppException):
    pass


class DatabaseError(AppException):
    pass