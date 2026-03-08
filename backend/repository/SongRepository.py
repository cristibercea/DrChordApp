from typing import Optional
import psycopg2
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

    def create(self, song: Song) -> Optional[Song]:
        """
        Adds a song to the database and returns the new song with its id set
        :param song: song to be created
        :return: the song created with the id set from the database
        :raises RepositoryException: if something went wrong while creating the song
        """
        conn = validate_and_connect(self.__database, self.__validator, song, self.__class__.__name__, "Error when creating song")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""INSERT INTO songs(user_id, name, genre, recording_path, date_recorded) 
                                  VALUES (%s, %s, %s, %s, %s) RETURNING id""", (song.get_user_id(), song.get_name(), song.get_genre(), song.get_recording_path(), song.get_recording_date()))
                result = cursor.fetchone()
                conn.commit()
                if result:
                    song.set_id(result[0])
                    return song
        except psycopg2.Error as e:
            conn.rollback()
            raise RepositoryException(self.__class__.__name__+ f": Error when creating song: {e}")

    def get_by_id(self, song_id: int) -> Optional[Song]:
        """
        Gets a song by its id from the database
        :param song_id: the id of the song to be retrieved
        :return: the song with the given id
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            with self.__database.get_connection().cursor() as cursor:
                cursor.execute("""SELECT id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated FROM songs WHERE id = %s""", (song_id,))
                result = cursor.fetchone()
                return Song(*result) if result else None
        except psycopg2.Error as e:
            raise RepositoryException(self.__class__.__name__+ f": Error when getting song by id {song_id}: {e}")

    def get_all_paged(self, limit: int, offset: int) -> list[Song]:
        """
        Gets a set amount of songs from the database
        :param limit: the maximum amount of songs to be returned
        :param offset: the start offset of the songs to be returned
        :return: a list of maximum <limit> songs starting from <offset>
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            with self.__database.get_connection().cursor() as cursor:
                cursor.execute("""SELECT id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated 
                                  FROM songs LIMIT %s OFFSET %s""", (limit, offset))
                result = cursor.fetchall()
                return [Song(*row) for row in result]
        except psycopg2.Error as e:
            raise RepositoryException(self.__class__.__name__+ f": Error when getting all songs: {e}")

    def find_by_name_paged(self, name: str, limit: int, offset: int) -> list[Song]:
        """
        Gets a set amount of songs from the database filtered by the given name
        :param name: the name of the songs to be returned
        :param limit: the maximum amount of songs to be returned
        :param offset: the start offset of the songs to be returned
        :return: a list of maximum <limit> songs starting from <offset> and having a certain name
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            with self.__database.get_connection().cursor() as cursor:
                cursor.execute("""SELECT id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated 
                                  FROM songs WHERE name LIKE %s LIMIT %s OFFSET %s""", (name, limit, offset))
                result = cursor.fetchall()
                return [Song(*row) for row in result]
        except psycopg2.Error as e:
            raise RepositoryException(self.__class__.__name__+ f": Error when finding songs: {e}")

    def update(self, song: Song) -> Optional[Song]:
        """
        Updates a song's data in the database
        :param song: the new version of a song
        :return: 'None' if the song was updated successfully, the new version of the song otherwise
        :raises RepositoryException: if something went wrong while updating the song's data
        """
        conn = validate_and_connect(self.__database, self.__validator, song, self.__class__.__name__, f"Error when updating song with id {song.get_id()}")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""UPDATE songs SET name = %s, genre = %s, recording_path = %s, date_recorded = %s, tabs_path = %s, date_generated = %s WHERE id = %s""",
                               (song.get_name(), song.get_genre(), song.get_recording_path(), song.get_recording_date(), song.get_tabs_path(), song.get_generated_date(), song.get_id()))
                conn.commit()
        except psycopg2.Error:
            conn.rollback()
            return song
        return None

    def delete(self, song_id: int) -> Optional[Song]:
        """
        Deletes a song in the database
        :param song_id: the id of the song to be deleted
        :return: the deleted song if the song was deleted successfully, 'None' otherwise
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try: conn = self.__database.get_connection()
        except psycopg2.Error as e: raise RepositoryException(self.__class__.__name__+ f": Error when deleting song: {e}")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""DELETE FROM songs WHERE id = %s RETURNING id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated""", (song_id,))
                deleted = cursor.fetchone()
                if deleted:
                    conn.commit()
                    return Song(*deleted)
        except psycopg2.Error as e:
            conn.rollback()
            raise RepositoryException(self.__class__.__name__+ f": Error when deleting song: {e}")
        return None
