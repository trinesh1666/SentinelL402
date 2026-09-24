from sqlalchemy.exc import SQLAlchemyError


class DatabaseServiceError(Exception):
    """Raised when the application cannot complete a database operation."""