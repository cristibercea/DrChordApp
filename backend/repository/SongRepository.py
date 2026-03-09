from typing import Optional
import asyncpg
from backend.domain.database.DrChordDatabase import DrChordDatabase
from backend.domain.entities.Song import Song
from backend.domain.utils.validation.SongValidator import SongValidator
from backend.repository.AbstractRepository import AbstractRepository
from backend.repository.RepositoyException import RepositoryException
from backend.repository.utils.validate_and_connect import validate_and_connect


class SongRepository(AbstractRepository):
    """The repository for the Song entity"""

    def __init__(self, database: DrChordDatabase):
        self.__database = database
        self.__validator = SongValidator()

    async def create(self, song: Song) -> Optional[Song]:
        """
        Adds a song to the database and returns the new song with its id set
        :param song: song to be created
        :return: the song created with the id set from the database
        :raises RepositoryException: if something went wrong while creating the song
        """
        conn = await validate_and_connect(self.__database, self.__validator, song, self.__class__.__name__, "Error when creating song")
        try:
            async with conn.transaction():
                result = await conn.fetchval("""INSERT INTO songs(user_id, name, genre, recording_path, date_recorded) 
                                      VALUES ($1, $2, $3, $4, $5) RETURNING id""", song.get_user_id(), song.get_name(), song.get_genre(), song.get_recording_path(), song.get_recording_date())
                if result:
                    song.set_id(result)
                    return song
        except asyncpg.PostgresError as e:
            raise RepositoryException(self.__class__.__name__+ f": Database error when creating song: {e}")
        except Exception as e:
            raise RepositoryException(self.__class__.__name__+ f": Unexpected error when creating song: {e}")

    async def get_by_id(self, song_id: int) -> Optional[Song]:
        """
        Gets a song by its id from the database
        :param song_id: the id of the song to be retrieved
        :return: the song with the given id
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            conn = await self.__database.get_connection()
            async with conn.transaction():
                result = await conn.fetchrow("""SELECT id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated FROM songs WHERE id = $1""", song_id)
                return Song(*result) if result else None
        except asyncpg.PostgresError as e:
            raise RepositoryException(self.__class__.__name__+ f": Database error when getting song by id {song_id}: {e}")
        except Exception as e:
            raise RepositoryException(self.__class__.__name__+ f": Unexpected error when getting song by id {song_id}: {e}")

    async def get_all_paged(self, limit: int, offset: int) -> list[Song]:
        """
        Gets a set amount of songs from the database
        :param limit: the maximum amount of songs to be returned
        :param offset: the start offset of the songs to be returned
        :return: a list of maximum <limit> songs starting from <offset>
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            conn = await self.__database.get_connection()
            async with conn.transaction():
                result = await conn.fetch("""SELECT id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated 
                                  FROM songs LIMIT $1 OFFSET $2""", limit, offset)
                return [Song(*row) for row in result]
        except asyncpg.PostgresError as e:
            raise RepositoryException(self.__class__.__name__ + f": Database error when getting all songs: {e}")
        except Exception as e:
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when getting all songs: {e}")

    async def find_by_name_paged(self, name: str, limit: int, offset: int) -> list[Song]:
        """
        Gets a set amount of songs from the database filtered by the given name
        :param name: the name of the songs to be returned
        :param limit: the maximum amount of songs to be returned
        :param offset: the start offset of the songs to be returned
        :return: a list of maximum <limit> songs starting from <offset> and having a certain name
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            conn = await self.__database.get_connection()
            async with conn.transaction():
                result = await conn.fetch("""SELECT id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated 
                                  FROM songs WHERE name LIKE $1 LIMIT $2 OFFSET $3""", f"%{name}%", limit, offset)
                return [Song(*row) for row in result]
        except asyncpg.PostgresError as e:
            raise RepositoryException(self.__class__.__name__ + f": Database error when finding songs: {e}")
        except Exception as e:
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when finding songs: {e}")

    async def update(self, song: Song) -> Optional[Song]:
        """
        Updates a song's data in the database
        :param song: the new version of a song
        :return: 'None' if the song was updated successfully, the new version of the song otherwise
        :raises RepositoryException: if something went wrong while updating the song's data
        """
        conn = await validate_and_connect(self.__database, self.__validator, song, self.__class__.__name__, f"Error when updating song with id {song.get_id()}")
        try:
            async with conn.transaction():
                status = await conn.execute("""UPDATE songs SET name = $1, genre = $2, recording_path = $3, date_recorded = $4, tabs_path = $5, date_generated = $6 WHERE id = $7""",
                               song.get_name(), song.get_genre(), song.get_recording_path(), song.get_recording_date(), song.get_tabs_path(), song.get_generated_date(), song.get_id())
                return song if status == "UPDATE 0" else None
        except Exception as e:
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when updating a song: {e}")

    async def delete(self, song_id: int) -> Optional[Song]:
        """
        Deletes a song in the database
        :param song_id: the id of the song to be deleted
        :return: the deleted song if the song was deleted successfully, 'None' otherwise
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            conn = await self.__database.get_connection()
            async with conn.transaction():
                deleted = await conn.fetchrow("""DELETE FROM songs WHERE id = $1 RETURNING id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated""", song_id)
                return Song(*deleted) if deleted else None
        except asyncpg.PostgresError as e:
            raise RepositoryException(self.__class__.__name__ + f": Database error when deleting song: {e}")
        except Exception as e:
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when deleting song: {e}")
