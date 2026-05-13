import asyncpg, logging
from backend.domain.database.DrChordDatabase import DrChordDatabase
from backend.domain.entities.Entity import Entity
from backend.domain.utils.validation.AbstractValidator import AbstractValidator
from backend.domain.utils.validation.ValidationException import ValidationException
from backend.repository.utils.RepositoyException import RepositoryException


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
        logging.info(f"[{class_name}]: Validating {entity.__class__.__name__} entity with id {entity.get_id()}.")
        validator.validate(entity)
        logging.info(f"[{class_name}]: {entity.__class__.__name__} entity with id {entity.get_id()} is valid!")
    except ValidationException as ve:
        logging.warning(f"[{class_name}]: {entity.__class__.__name__} entity with id {entity.get_id()} is not valid: {ve}")
        raise RepositoryException(class_name + ": " + str(ve))
    try:
        logging.info(f"[{class_name}]: Connecting to the DrChord Database...")
        return await database.get_connection()
    except asyncpg.PostgresError as e:
        msg = operation_failed_string if operation_failed_string else "Database error"
        logging.error(f"[{class_name}]: Failed to connect to the DrChord Database: {msg}")
        raise RepositoryException(class_name + ": " + msg + f": {e}")
    except Exception as e:
        msg = operation_failed_string if operation_failed_string else "Unexpected error"
        logging.error(f"[{class_name}]: Failed to connect to the DrChord Database: {msg}")
        raise RepositoryException(class_name + ": " + msg + f": {e}")
