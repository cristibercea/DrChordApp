import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from backend.repository.UserRepository import UserRepository  # Presupunem că aici e logica de asyncpg
from utils.config_reader import config
from backend.domain.entities.User import User
from backend.service.utils.ServiceException import ServiceException
from repository.RepositoyException import RepositoryException


def _create_access_token(data: dict):
    to_encode = data.copy()
    conf = config(section="security")
    expire = datetime.now() + timedelta(minutes=float(str(conf["access_token_expire_mins"])))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, str(conf["secret"]), algorithm=str(conf["algorithm"]))


def _verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def _get_password_hash(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.__repo = user_repo

    async def register_user(self, name: str, email: str, password: str):
        password = _get_password_hash(password)
        try:
            new_user = await self.__repo.create(User(-1, name, email, password, datetime.now()))
            return {"user": new_user, "status": 201}
        except RepositoryException as e: raise ServiceException(e)

    async def authenticate_user(self, email, password):
        user = await self.__repo.get_by_email(email)
        if not user or not _verify_password(password, user.get_password()): raise ServiceException("Incorrect email or password")
        token = _create_access_token({"sub": str(user.get_id()), "email": user.get_email()})
        return {"user": {"id": user.get_id(), "name": user.get_name(), "email": user.get_email()}, "token": token}

    async def update_user(self, user_id: int, name: str = None, current_password: str = None, new_password: str = None):
        existing_user = await self.__repo.get_by_id(user_id)
        if not existing_user: raise ServiceException("User not found.")

        final_name = name if name and name.strip() else existing_user.get_name()
        final_password = existing_user.get_password()

        if new_password and new_password.strip():
            if not current_password or not _verify_password(current_password, final_password):
                raise ServiceException("Current password is incorrect.")
            final_password = _get_password_hash(new_password)

        updated_user_obj = User(
            user_id,
            final_name,
            existing_user.get_email(),
            final_password,
            existing_user.get_date_joined()
        )
        result = await self.__repo.update(updated_user_obj)
        if result is not None: raise ServiceException("Failed to update user.")
        return updated_user_obj

    async def delete_user(self, user_id: int):
        deleted_user = await self.__repo.delete(user_id)
        if not deleted_user: raise ServiceException("User not found or already deleted.")
        return deleted_user