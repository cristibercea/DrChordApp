from datetime import datetime
from backend.domain.entities.Entity import Entity


class Song(Entity):
    __id: int
    __user_id: int
    __name: str
    __recording_path: str
    __recording_date: datetime
    __tabs_path: str | None
    __generated_date: datetime | None

    def __init__(self, sid: int, user_id: int, name: str, genre: str, recording_path: str, recording_date: datetime, tabs_path: str | None = None, generated_date: datetime | None = None):
        self.__id = sid
        self.__user_id = user_id
        self.__name = name
        self.__genre = genre
        self.__recording_path = recording_path
        self.__recording_date = recording_date
        self.__tabs_path = tabs_path
        self.__generated_date = generated_date

    def get_id(self) -> int: return self.__id
    def get_user_id(self) -> int: return self.__user_id
    def get_name(self) -> str: return self.__name
    def get_genre(self) -> str: return self.__genre
    def get_recording_path(self) -> str: return self.__recording_path
    def get_recording_date(self) -> datetime: return self.__recording_date
    def get_tabs_path(self) -> str | None: return self.__tabs_path
    def get_generated_date(self) -> datetime | None: return self.__generated_date

    def set_id(self, new_id: int) -> None: self.__id = new_id
    def set_name(self, new_name: str) -> None: self.__name = new_name
    def set_genre(self, new_genre: str) -> None: self.__genre = new_genre
    def set_tabs_path(self, new_tabs_path: str) -> None: self.__tabs_path = new_tabs_path
    def set_generated_date(self, new_generated_date: datetime) -> None: self.__generated_date = new_generated_date

    def __str__(self) -> str: return f'Song {self.__id}: [Name: {self.__name} | Genre: {self.__genre} | Recorded on: {self.__recording_date} | Tabs Generated: {"yes" if self.__generated_date else "no"}]'
