from datetime import datetime
from backend.domain.entities.Entity import Entity


class User(Entity):
    __id: int
    __name: str
    __email: str
    __password: str
    __date_joined: datetime

    def __init__(self, uid: int, name: str, email: str, password: str, date_joined: datetime):
        self.__id = uid
        self.__name = name
        self.__email = email
        self.__password = password
        self.__date_joined = date_joined

    def get_id(self) -> int: return self.__id
    def get_name(self) -> str: return self.__name
    def get_email(self) -> str: return self.__email
    def get_password(self) -> str: return self.__password
    def get_date_joined(self) -> datetime: return self.__date_joined

    def set_id(self, new_id: int) -> None: self.__id = new_id
    def set_name(self, new_name: str) -> None: self.__name = new_name
    def set_email(self, new_email: str) -> None: self.__email = new_email
    def set_password(self, new_password: str) -> None: self.__password = new_password
    def set_date_joined(self, new_date_joined) -> None: self.__date_joined = new_date_joined

    def __str__(self) -> str: return f'User {self.__id}: [Name: {self.__name} | Email: {self.__email} | Registered in: {self.__date_joined}]'
