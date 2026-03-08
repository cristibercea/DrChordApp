from typing import Optional
import psycopg2
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

    def create(self, user: User) -> Optional[User]:
        """
        Adds a user to the database and returns the new user with its id set
        :param user: user to be created
        :return: the user created with the id set from the database
        :raises RepositoryException: if something went wrong while creating the user
        """
        conn = validate_and_connect(self.__database, self.__validator, user, self.__class__.__name__, "Error when creating user")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""INSERT INTO users (name, email, password, date_joined) 
                                  VALUES (%s, %s, %s, %s) RETURNING id""", (user.get_name(), user.get_email(), user.get_password(), user.get_date_joined()))
                result = cursor.fetchone()
                conn.commit()
                if result:
                    user.set_id(result[0])
                    return user
        except psycopg2.Error as e:
            conn.rollback()
            raise RepositoryException(self.__class__.__name__+ f": Error when creating user: {e}")

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Gets a user by its id from the database
        :param user_id: the id of the user to be retrieved
        :return: the user with the given id
        :raises RepositoryException: if something went wrong while communicating with the database
                """
        try:
            with self.__database.get_connection().cursor() as cursor:
                cursor.execute("SELECT id, name, email, password, date_joined FROM users WHERE id = %s", (user_id,))
                result = cursor.fetchone()
                return User(*result) if result else None
        except psycopg2.Error as e:
            raise RepositoryException(self.__class__.__name__+ f": Error when getting user by id {user_id}: {e}")


    def find_by_name_paged(self, name: str, limit: int, offset: int) -> list[User]:
        """
        Gets a set amount of users from the database filtered by the given name
        :param name: the name of the users to be returned
        :param limit: the maximum amount of users to be returned
        :param offset: the start offset of the users to be returned
        :return: a list of maximum <limit> users starting from <offset> and having a certain name
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            with self.__database.get_connection().cursor() as cursor:
                cursor.execute("""SELECT id, name, email, password, date_joined FROM users 
                                  WHERE name LIKE %s LIMIT %s, OFFSET %s""", (name, limit, offset))
                result = cursor.fetchall()
                return [User(*row) for row in result]
        except psycopg2.Error as e:
            raise RepositoryException(self.__class__.__name__+ f": Error when getting users by name {name}: {e}")

    def update(self, user: User) -> Optional[User]:
        """
        Updates a user's data in the database
        :param user: the new version of a user
        :return: 'None' if the user was updated successfully, the new version of the user otherwise
        :raises RepositoryException: if something went wrong while updating the user's data
        """
        conn = validate_and_connect(self.__database, self.__validator, user, self.__class__.__name__, "Error when updating user")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""UPDATE users SET name = %s, email = %s, password = %s, date_joined = %s WHERE id = %s""",
                               (user.get_name(), user.get_email(), user.get_password(), user.get_date_joined(), user.get_id()))
                conn.commit()
        except psycopg2.Error:
            conn.rollback()
            return user
        return None

    def delete(self, user_id: int) -> Optional[User]:
        """
        Deletes a user in the database
        :param user_id: the id of the user to be deleted
        :return: the deleted user if the user was deleted successfully, 'None' otherwise
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try: conn = self.__database.get_connection()
        except psycopg2.Error as e: raise RepositoryException(self.__class__.__name__+ f": Error when deleting user: {e}")
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s RETURNING id, name, email, password, date_joined", (user_id,))
                deleted = cursor.fetchone()
                if deleted:
                    conn.commit()
                    return User(*deleted)
        except psycopg2.Error as e:
            conn.rollback()
            raise RepositoryException(self.__class__.__name__+ f": Error when deleting user: {e}")
        return None
