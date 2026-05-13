import asyncpg, logging
from typing import Optional
from backend.domain.database.DrChordDatabase import DrChordDatabase
from backend.domain.entities.Song import Song
from backend.domain.utils.validation.SongValidator import SongValidator
from backend.repository.AbstractRepository import AbstractRepository
from backend.repository.utils.RepositoyException import RepositoryException
from backend.repository.utils.validate_and_connect import validate_and_connect


class SongRepository(AbstractRepository):
    """The repository for the Song entity"""

    def __init__(self, database: DrChordDatabase):
        """
        Initializes the Song repository
        :param database: DrChord app database
        """
        self.__database = database
        self.__validator = SongValidator()

    async def get_by_id(self, song_id: int) -> Optional[Song]:
        """
        Gets a song by its id from the database
        :param song_id: the id of the song to be retrieved
        :return: the song with the given id
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            logging.info(f"[{self.__class__.__name__}]: Connecting to the DrChord Database...")
            conn = await self.__database.get_connection()
            logging.info(f"[{self.__class__.__name__}]: Connected to DrChord Database.")
            async with conn.transaction():
                result = await conn.fetchrow("""SELECT id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated, midi_path, midi_date FROM songs WHERE id = $1""", song_id)
                logging.info(f"[{self.__class__.__name__}]: Returned the song with id {song_id}." if result else f"[{self.__class__.__name__}]: Returned None.")
                return Song(*result) if result else None
        except asyncpg.PostgresError as e:
            logging.error(f"[{self.__class__.__name__}]: Database error when getting song by id {song_id}: {e}")
            raise RepositoryException(self.__class__.__name__+ f": Database error when getting song by id {song_id}: {e}")
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}]: Unexpected error when getting the song: {e}")
            raise RepositoryException(self.__class__.__name__+ f": Unexpected error when getting song by id {song_id}: {e}")

    async def get_all_paged_by_user_id(self, user_id: int, limit: int, offset: int) -> list[Song]:
        """
        Gets a set amount of songs from the database
        :param user_id: the id of the user whose songs to be retrieved
        :param limit: the maximum amount of songs to be returned
        :param offset: the start offset of the songs to be returned
        :return: a list of maximum <limit> songs starting from <offset>
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            logging.info(f"[{self.__class__.__name__}]: Connecting to the DrChord Database...")
            conn = await self.__database.get_connection()
            logging.info(f"[{self.__class__.__name__}]: Connected to DrChord Database.")
            async with conn.transaction():
                result = await conn.fetch("""SELECT id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated, midi_path, midi_date 
                                  FROM songs WHERE user_id = $1 LIMIT $2 OFFSET $3""", user_id, limit, offset)
                logging.info(f"[{self.__class__.__name__}]: Returned {len(result)} songs for the user with id {user_id}.")
                return [Song(*row) for row in result]
        except asyncpg.PostgresError as e:
            logging.error(f"[{self.__class__.__name__}]: Database error when getting all songs: {e}")
            raise RepositoryException(self.__class__.__name__ + f": Database error when getting all songs: {e}")
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}]: Unexpected error when getting all songs: {e}")
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when getting all songs: {e}")

    async def find_paged_filtered(self, user_id: int, search: str | None, genre: str | None, hasTab: str | None, sortBy: str | None, limit: int, offset: int) -> list[Song]:
        """
        Finds songs filtered by the given parameters
        :param user_id: user id
        :param search: name search string
        :param genre: song genre
        :param hasTab: 'hasTabs' if the song has generated tabs
        :param sortBy: category by which the sort will be made
        :param limit: the maximum amount of songs to be returned
        :param offset: the start offset of the songs to be returned
        :return: a filtered and/or ordered list of songs
        """
        try:
            logging.info(f"[{self.__class__.__name__}]: Connecting to the DrChord Database...")
            conn = await self.__database.get_connection()
            logging.info(f"[{self.__class__.__name__}]: Connected to DrChord Database.")
            async with conn.transaction():
                query = """SELECT id,user_id,name,genre,recording_path,date_recorded,tabs_path,date_generated,midi_path,midi_date
                        FROM songs WHERE user_id = $1"""
                params = [user_id]
                param_index = 2  # Next parameter number
                # filter: search by name (optional)
                if search:
                    query += f" AND name ILIKE ${param_index}"
                    params.append(f"%{search}%")
                    param_index += 1
                # filter: genre (optional)
                if genre:
                    query += f" AND genre ILIKE ${param_index}"
                    params.append(f"%{genre}%")
                    param_index += 1
                # filter: has tabs or not (optional)
                if hasTab == "yes": query += " AND tabs_path IS NOT NULL"
                elif hasTab == "no": query += " AND tabs_path IS NULL"
                # sort types (optional)
                if sortBy == "name_asc": query += " ORDER BY name ASC"
                elif sortBy == "name_desc": query += " ORDER BY name DESC"
                elif sortBy == "date_asc": query += " ORDER BY date_recorded ASC"
                else: query += " ORDER BY date_recorded DESC"  # Default
                # build the final query (safe against SQL Injections)
                query += f" LIMIT ${param_index} OFFSET ${param_index + 1}"
                params.extend([limit, offset])
                logging.info(f"[{self.__class__.__name__}]: Fetching songs...")
                # load all parameters and run the query
                result = await conn.fetch(query, *params)
                logging.info(f"[{self.__class__.__name__}]: Returned {len(result)} filtered songs for the user with id {user_id}.")
                return [Song(*row) for row in result]
        except asyncpg.PostgresError as e:
            logging.error(f"[{self.__class__.__name__}]: Database error when finding filtered songs: {e}")
            raise RepositoryException(self.__class__.__name__ + f": Database error when finding filtered songs: {e}")
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}]: Unexpected error when finding filtered songs: {e}")
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when finding filtered songs: {e}")

    async def create(self, song: Song) -> Optional[Song]:
        """
        Adds a song to the database and returns the new song with its id set
        :param song: song to be created
        :return: the song created with the id set from the database
        :raises RepositoryException: if something went wrong while creating the song
        """
        conn = await validate_and_connect(self.__database, self.__validator, song, self.__class__.__name__, "Error when creating song")
        logging.info(f"[{self.__class__.__name__}]: Connected to DrChord Database.")
        try:
            async with conn.transaction():
                result = await conn.fetchval("""INSERT INTO songs(user_id, name, genre, recording_path, date_recorded, midi_path, midi_date) 
                                      VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id""", song.get_user_id(), song.get_name(), song.get_genre(), song.get_recording_path(), song.get_recording_date(), song.get_midi_path(), song.get_midi_date())
                if result:
                    song.set_id(result)
                    logging.info(f"[{self.__class__.__name__}]: Created song with id {song.get_id()}.")
                    return song
                logging.warning(f"[{self.__class__.__name__}]: Failed to create song.")
        except asyncpg.PostgresError as e:
            logging.error(f"[{self.__class__.__name__}]: Database error when creating song: {e}")
            raise RepositoryException(self.__class__.__name__+ f": Database error when creating song: {e}")
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}]: Unexpected error when creating song: {e}")
            raise RepositoryException(self.__class__.__name__+ f": Unexpected error when creating song: {e}")

    async def update(self, song: Song) -> Optional[Song]:
        """
        Updates a song's data in the database
        :param song: the new version of a song
        :return: 'None' if the song was updated successfully, the new version of the song otherwise
        :raises RepositoryException: if something went wrong while updating the song's data
        """
        conn = await validate_and_connect(self.__database, self.__validator, song, self.__class__.__name__, f"Error when updating song with id {song.get_id()}")
        logging.info(f"[{self.__class__.__name__}]: Connected to DrChord Database.")
        try:
            async with conn.transaction():
                status = await conn.execute("""UPDATE songs SET name = $1, genre = $2, recording_path = $3, date_recorded = $4, tabs_path = $5, date_generated = $6, midi_path = $7, midi_date = $8 WHERE id = $9""",
                               song.get_name(), song.get_genre(), song.get_recording_path(), song.get_recording_date(), song.get_tabs_path(), song.get_generated_date(), song.get_midi_path(), song.get_midi_date(), song.get_id())
                logging.info(f"[{self.__class__.__name__}]: Updated song with id {song.get_id()}." if status != "UPDATE 0" else f"[{self.__class__.__name__}]: Failed to update song with id {song.get_id()}.")
                return song if status == "UPDATE 0" else None
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}]: Unexpected error when updating song: {e}")
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when updating a song: {e}")

    async def delete(self, song_id: int) -> Optional[Song]:
        """
        Deletes a song in the database
        :param song_id: the id of the song to be deleted
        :return: the deleted song if the song was deleted successfully, 'None' otherwise
        :raises RepositoryException: if something went wrong while communicating with the database
        """
        try:
            logging.info(f"[{self.__class__.__name__}]: Connecting to DrChord Database...")
            conn = await self.__database.get_connection()
            logging.info(f"[{self.__class__.__name__}]: Connected to DrChord Database.")
            async with conn.transaction():
                deleted = await conn.fetchrow("""DELETE FROM songs WHERE id = $1 RETURNING id, user_id, name, genre, recording_path, date_recorded, tabs_path, date_generated, midi_path, midi_date""", song_id)
                logging.info(f"[{self.__class__.__name__}]: Deleted song with id {song_id}." if deleted else f"[{self.__class__.__name__}]: Failed to delete song with id {song_id}.")
                return Song(*deleted) if deleted else None
        except asyncpg.PostgresError as e:
            logging.error(f"[{self.__class__.__name__}]: Database error when deleting song: {e}")
            raise RepositoryException(self.__class__.__name__ + f": Database error when deleting song: {e}")
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}]: Unexpected error when deleting song: {e}")
            raise RepositoryException(self.__class__.__name__ + f": Unexpected error when deleting song: {e}")
