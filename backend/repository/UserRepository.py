from typing import Optional
import asyncpg
from backend.domain.database.DrChordDatabase import DrChordDatabase
from backend.domain.entities.User import User
from backend.domain.utils.validation.UserValidator import UserValidator
from backend.repository.AbstractRepository import AbstractRepository
from backend.repository.RepositoyException import RepositoryException
from backend.repository.utils.validate_and_connect import validate_and_connect


class UserRepository(AbstractRepository):
    """The repository for the User entity"""

    def __init__(self, database: DrChordDatabase):
        self.__database = database
        self.__validator = UserValidator()

    async def create(self, user: User) -> Optional[User]:
        """
        Adds a user to the database and returns the new user with its id set
        :param user: user to be created
        :return: the user created with the id set from the database
        :raises RepositoryException: if something went wrong while creating the user
        """
        conn = await validate_and_connect(self.__database, self.__validator, user, self.__class__.__name__, "Error when creating user")
        try:
            async with conn.transaction():
                result = await conn.fetchval("""INSERT INTO users (name, email, password, date_joined) 
                                  VALUES ($1, $2, $3, $4) RETURNING id""", user.get_name(), user.get_email(), user.get_password(), user.get_date_joined())
                if result:
                    user.set_id(result)
                    return user
        except asyncpg.PostgresError as e:
            raise RepositoryException(self.__class__.__name__ + f": Database error when creating user: {e}")
        except Exception as e:
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when creating user: {e}")

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Gets a user by its id from the database
        :param user_id: the id of the user to be retrieved
        :return: the user with the given id
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            conn = await self.__database.get_connection()
            async with conn.transaction():
                result = await conn.fetchrow("SELECT id, name, email, password, date_joined FROM users WHERE id = $1", user_id)
                return User(*result) if result else None
        except asyncpg.PostgresError as e:
            raise RepositoryException(self.__class__.__name__ + f": Database error when getting user by id {user_id}: {e}")
        except Exception as e:
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when getting user by id {user_id}: {e}")

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Gets a user by its email from the database
        :param email: the email of the user to be retrieved
        :return: the user with the given email
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            conn = await self.__database.get_connection()
            async with conn.transaction():
                result = await conn.fetchrow("SELECT id, name, email, password, date_joined FROM users WHERE email = $1", email)
                return User(*result) if result else None
        except asyncpg.PostgresError as e:
            raise RepositoryException(self.__class__.__name__ + f": Database error when getting user by email {email}: {e}")
        except Exception as e:
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when getting user by email {email}: {e}")

    async def find_by_name_paged(self, name: str, limit: int, offset: int) -> list[User]:
        """
        Gets a set amount of users from the database filtered by the given name
        :param name: the name of the users to be returned
        :param limit: the maximum amount of users to be returned
        :param offset: the start offset of the users to be returned
        :return: a list of maximum <limit> users starting from <offset> and having a certain name
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            conn = await self.__database.get_connection()
            async with conn.transaction():
                result = await conn.fetch("""SELECT id, name, email, password, date_joined FROM users 
                                  WHERE name LIKE $1 LIMIT $2 OFFSET $3""", f"{name}%", limit, offset)
                return [User(*row) for row in result]
        except asyncpg.PostgresError as e:
            raise RepositoryException(self.__class__.__name__ + f": Database error when finding users: {e}")
        except Exception as e:
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when finding users: {e}")

    async def update(self, user: User) -> Optional[User]:
        """
        Updates a user's data in the database
        :param user: the new version of a user
        :return: 'None' if the user was updated successfully, the new version of the user otherwise
        :raises RepositoryException: if something went wrong while updating the user's data
        """
        conn = await validate_and_connect(self.__database, self.__validator, user, self.__class__.__name__, "Error when updating user")
        try:
            async with conn.transaction():
                status = await conn.execute("""UPDATE users SET name = $1, email = $2, password = $3, date_joined = $4 WHERE id = $5""",
                               user.get_name(), user.get_email(), user.get_password(), user.get_date_joined(), user.get_id())
                return user if status == "UPDATE 0" else None
        except Exception as e:
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when updating a user: {e}")

    async def delete(self, user_id: int) -> Optional[User]:
        """
        Deletes a user in the database
        :param user_id: the id of the user to be deleted
        :return: the deleted user if the user was deleted successfully, 'None' otherwise
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            conn = await self.__database.get_connection()
            async with conn.transaction():
                deleted = await conn.fetchrow("DELETE FROM users WHERE id = $1 RETURNING id, name, email, password, date_joined", user_id)
                return User(*deleted) if deleted else None
        except asyncpg.PostgresError as e:
            raise RepositoryException(self.__class__.__name__ + f": Database error when deleting user: {e}")
        except Exception as e:
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when deleting user: {e}")
