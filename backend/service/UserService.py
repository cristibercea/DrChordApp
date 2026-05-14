import bcrypt, logging
from jose import jwt
from datetime import datetime, timedelta
from backend.domain.entities.User import User
from backend.utils.config_reader import config
from backend.repository.UserRepository import UserRepository
from backend.service.utils.ServiceException import ServiceException
from backend.repository.utils.RepositoyException import RepositoryException

def _create_access_token(data: dict) -> str:
    """
    Creates the JWT access token using the app.ini configuration and user data.
    :param data: user data
    :return: the JWT access token
    """
    logging.info(f"Creating JWT access token for user with email {data['email']}...")
    to_encode = data.copy()
    try: conf = config(section="security")
    except FileNotFoundError | RuntimeError as e:
        logging.fatal(e)
        raise ServiceException(e)
    expire = datetime.now() + timedelta(minutes=float(str(conf["access_token_expire_mins"])))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, str(conf["secret"]), algorithm=str(conf["algorithm"]))

def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the plain_password and hashed_password are the same.
    :param plain_password: the plain text password to verify
    :param hashed_password: the encrypted password from the database
    :return: true if the plain_password and hashed_password are the same, false otherwise
    """
    logging.info("Verifying if the plaintext password and the hashed password are equal...")
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def _get_password_hash(password: str) -> str:
    """
    Encrypts the given password.
    :param password: the password to encrypt
    :return: encrypted password
    """
    logging.info(f"Encrypting user password...")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


class UserService:
    """SongService class - responsible with managing user entities"""
    def __init__(self, user_repo: UserRepository):
        self.__repo = user_repo
        self.__pending_user_registrations = {}

    def get_pending_user_registration(self, user_email: str) -> dict | None:
        """
        Gets a pending user's registration data from the service temporary storage.
        :param user_email: the email of the user whose registration to be retrieved
        :return: the registration data if it exists
        """
        return self.__pending_user_registrations.get(user_email)

    def add_pending_user_registration(self, user_email: str, registration_data: dict) -> None:
        """
        Adds a pending user's registration data to the service temporary storage.
        :param user_email: the email of the user to be registered
        :param registration_data: the data pending registration
        :return: None
        """
        self.__pending_user_registrations[user_email] = registration_data

    def delete_pending_user_registration(self, user_email: str) -> None:
        """
        Deletes a pending user's registration data from the service temporary storage.
        :param user_email: the email of the user whose registration to be deleted
        :return: None
        """
        del self.__pending_registrations[user_email]

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Gets a user object by id from the database if it exists.
        :param user_id: id of the user to be retrieved
        :return: the desired user object
        """
        try:
            logging.info(f"[{self.__class__.__name__}]: Getting user with id {user_id}...")
            return await self.__repo.get_by_id(user_id)
        except RepositoryException as e:
            logging.error(f"[{self.__class__.__name__}]: Failed to get user with id {user_id}: {e}")
            raise ServiceException(e)

    async def get_by_email(self, email: str) -> User | None:
        """
        Gets a user object by email from the database if it exists.
        :param email: email of the user to be retrieved
        :return: the desired user object
        """
        try:
            logging.info(f"[{self.__class__.__name__}]: Getting user with email {email}...")
            return await self.__repo.get_by_email(email)
        except RepositoryException as e:
            logging.error(f"[{self.__class__.__name__}]: Failed to get user with email {email}: {e}")
            raise ServiceException(e)

    async def register_user(self, name: str, email: str, password: str) -> dict:
        """
        Registers a new user with the given name, email and password.
        :param name: the name of the user
        :param email: the email of the user
        :param password: the password of the user
        :return: {"user": new_user, "status": 201} - a dictionary containing the new user's data with the OK Web Status
        """
        logging.info(f"[{self.__class__.__name__}]: Registering user with email {email}...")
        password = _get_password_hash(password)
        logging.info(f"Encrypted user password.")
        try:
            logging.info(f"[{self.__class__.__name__}]: Creating user with email {email}...")
            new_user = await self.__repo.create(User(-1, name, email, password, datetime.now()))
            logging.info(f"[{self.__class__.__name__}]: Created user with email {email}...")
            return {"user": new_user, "status": 201}
        except RepositoryException as e:
            logging.error(f"[{self.__class__.__name__}]: Failed to create user with email {email}: {e}")
            raise ServiceException(e)

    async def authenticate_user(self, email: str, password: str) -> dict:
        """
        Authenticates a user with the given email and password.
        :param email: the email of the user
        :param password: the password of the user
        :return: {"user": {"id": user_id, "name": user_name, "email": user_email}, "token": JWT} - a dictionary
        containing the authenticated user's data with JWT
        """
        logging.info(f"[{self.__class__.__name__}]: Authenticating user with email {email}...")
        try:
            user = await self.__repo.get_by_email(email)
            logging.info(f"[{self.__class__.__name__}]: Found user with email {email}...")
            if not user or not _verify_password(password, user.get_password()):
                logging.warning(f"The credentials for {email} and {password} are incorrect.")
                raise ServiceException("Incorrect email or password")
            logging.info(f"The credentials for {email} and {password} are correct.")
            token = _create_access_token({"sub": str(user.get_id()), "email": user.get_email()})
            logging.info(f"Created JWT access token for user with email {user.get_email()}...")
            logging.info(f"[{self.__class__.__name__}]: Authenticated user with email {email}.")
            return {"user": {"id": user.get_id(), "name": user.get_name(), "email": user.get_email()}, "token": token}
        except RepositoryException as e:
            logging.error(f"[{self.__class__.__name__}]: Failed to authenticate user with email {email}: {e}")
            raise ServiceException(e)

    async def update_user(self, user_id: int, new_name: str = None, current_password: str = None, new_password: str = None) -> User:
        """
        Updates the user object with the given id from the database if it exists.
        :param user_id: the id of the user to be updated
        :param new_name: the new name of the user
        :param current_password: the current password of the user
        :param new_password: the new password of the user
        :return: the updated user's data
        """
        logging.info(f"[{self.__class__.__name__}]: Updating user with id {user_id}...")
        try: existing_user = await self.__repo.get_by_id(user_id)
        except RepositoryException as e:
            logging.error(f"[{self.__class__.__name__}]: Failed to update user with id {user_id}: {e}")
            raise ServiceException(e)
        if not existing_user:
            logging.warning(f"[{self.__class__.__name__}]: There is no user with id {user_id} in the database.")
            raise ServiceException("User not found.")

        logging.info(f"[{self.__class__.__name__}]: Found user with id {user_id}. Updating...")
        final_name = new_name if new_name and new_name.strip() else existing_user.get_name()
        final_password = existing_user.get_password()

        if new_password and new_password.strip():
            if not current_password or not _verify_password(current_password, final_password):
                logging.warning(f"The credentials for {final_name} and {final_password} are incorrect.")
                raise ServiceException("Current password is incorrect.")
            logging.info(f"The credentials for {final_name} are correct.")
            final_password = _get_password_hash(new_password)
            logging.info(f"Encrypted a new password for user with email {final_name}.")

        updated_user_obj = User(
            user_id,
            final_name,
            existing_user.get_email(),
            final_password,
            existing_user.get_date_joined()
        )
        logging.info(f"Updating user with email {existing_user.get_email()}.")
        try:
            result = await self.__repo.update(updated_user_obj)
            if result is not None:
                logging.info(f"Failed to update user with email {existing_user.get_email()}.")
                raise ServiceException("Failed to update user.")
        except RepositoryException as e:
            logging.error(f"Failed to update user with email {existing_user.get_email()} : {e}")
            raise ServiceException(e)
        logging.info(f"Updated user with email {existing_user.get_email()}.")
        return updated_user_obj

    async def delete_user(self, user_id: int) -> User:
        """
        Deletes the user with the given id from the database.
        :param user_id: the id of the user to be deleted
        :return: the deleted user's data
        """
        logging.info(f"[{self.__class__.__name__}]: Deleting user with id {user_id}...")
        try: deleted_user = await self.__repo.delete(user_id)
        except RepositoryException as e:
            logging.warning(f"[{self.__class__.__name__}]: Failed to delete user with id {user_id}: {e}")
            raise ServiceException(e)
        if not deleted_user:
            logging.warning(f"[{self.__class__.__name__}]: Failed to delete user with id {user_id}.")
            raise ServiceException("User not found or already deleted.")
        logging.info(f"[{self.__class__.__name__}]: Deleted user with id {user_id}.")
        return deleted_user
