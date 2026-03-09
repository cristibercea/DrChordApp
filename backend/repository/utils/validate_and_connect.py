import asyncpg
from backend.domain.database.DrChordDatabase import DrChordDatabase
from backend.domain.entities.Entity import Entity
from backend.domain.utils.validation.AbstractValidator import AbstractValidator
from backend.domain.utils.validation.ValidationException import ValidationException
from backend.repository.RepositoyException import RepositoryException


async def validate_and_connect(database: DrChordDatabase, validator: AbstractValidator, entity: Entity, class_name: str, operation_failed_string: str | None = None) -> asyncpg.Connection:
    """
    Validate an entity and return a connection to the DrChordDatabase
    :param database: database to connect to
    :param validator: validator to use
    :param entity: entity to validate
    :param class_name: the name of the class where this function is called
    :param operation_failed_string: error message to raise if connection fails
    :return: the connection to the DrChordDatabase
    :raises RepositoryException: if the connection fails and if the entity validation fails
    """
    try:
        validator.validate(entity)
    except ValidationException as ve:
        raise RepositoryException(class_name + ": " + str(ve))
    try:
        return await database.get_connection()
    except asyncpg.PostgresError as e:
        msg = operation_failed_string if operation_failed_string else "Database error"
        raise RepositoryException(class_name + ": " + msg + f": {e}")
    except Exception as e:
        msg = operation_failed_string if operation_failed_string else "Unexpected error"
        raise RepositoryException(class_name + ": " + msg + f": {e}")