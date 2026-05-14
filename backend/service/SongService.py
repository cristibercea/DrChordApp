import os, json, logging
from typing import List
from datetime import datetime
from fastapi import UploadFile
from backend.domain.entities.Song import Song
from backend.service.utils import DocumentGenerator
from backend.service.FileService import FileService
from backend.repository.SongRepository import SongRepository
from backend.service.InferenceService import InferenceService
from backend.service.utils.ConnectionManager import ws_manager
from backend.service.utils.ServiceException import ServiceException
from repository.utils.RepositoyException import RepositoryException


class SongService:
    """SongService class - responsible with managing song entities"""
    def __init__(self, song_repo: SongRepository, file_service: FileService, inference_service: InferenceService):
        self.__repo = song_repo
        self.__file_service = file_service
        self.__inference_service = inference_service
        self.__allowed_extensions = ["mp3", "wav", "ogg", "flac"]
        self.__mime_types = { # Newly downloaded tabs' MIME Types (headers) for the browser
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "odt": "application/vnd.oasis.opendocument.text"
        }

    async def get_user_songs(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Song]:
        """
        Gets a maximum of 'limit' songs belonging to a user, starting with the 'offset'th song.
        :param user_id: the id of the user to get songs for
        :param limit: the maximum amount of songs to return
        :param offset: the offset to start getting songs from
        :return: a list of Song objects
        """
        logging.info(f"[{self.__class__.__name__}]: Getting songs for user {user_id}...")
        try: return await self.__repo.get_all_paged_by_user_id(user_id, limit, offset)
        except RepositoryException as e:
            logging.error(f"[{self.__class__.__name__}]: Failed to get songs for user {user_id}.")
            raise ServiceException(e)

    async def get_user_songs_filtered(self, user_id: int, search: str | None, genre: str | None, hasTab: str | None ,sortBy: str | None, limit: int, offset: int) -> List[Song]:
        """
        Gets a maximum of 'limit' songs belonging to a user, starting with the 'offset'th song, filtered by the given
        search term in the song name, their genre, and by the property of having a tab or not. They will be sorted by
        the SortBy parameter (defaults to 'date_desc').
        :param user_id: the id of the user to get songs for
        :param search: a search term from songs' names to filter the list songs by (optional parameter)
        :param genre: the genre to filter the list songs by (optional parameter)
        :param hasTab: the property of having a tab or not (optional parameter)
        :param sortBy: the sort method (optional parameter)
        :param limit: the maximum amount of filtered songs to return
        :param offset: the offset to start getting filtered songs from
        :return: a list of filtered Song objects
        """
        logging.info(f"[{self.__class__.__name__}]: Getting filtered songs for user {user_id}...")
        try: return await self.__repo.find_paged_filtered(user_id, search, genre, hasTab, sortBy, limit, offset)
        except RepositoryException as e:
            logging.error(f"[{self.__class__.__name__}]: Failed to get filtered songs for user {user_id}.")
            raise ServiceException(e)

    async def create_song(self, user_id: int, name: str, genre: str, file: UploadFile) -> Song:
        """
        Creates a new song with the given name, genre and uploaded audio file's name.
        :param user_id: the id of the user to create the new song for
        :param name: the name of the new song
        :param genre: the genre of the new song
        :param file: the uploaded audio file's name
        :return: the created Song object
        """
        logging.info(f"[{self.__class__.__name__}]: Verifying if there is an audio file for the song with name {name}...")
        if not file.filename:
            logging.warning(f"[{self.__class__.__name__}]: There is no audio file for the given song.")
            raise ServiceException("No file provided")
        logging.info(f"[{self.__class__.__name__}]: File presence checked.")
        ext = file.filename.split('.')[-1].lower()
        logging.info(f"[{self.__class__.__name__}]: Checking audio file extension...")
        if ext not in self.__allowed_extensions:
            logging.warning(f"[{self.__class__.__name__}]: Audio file extension not supported.")
            raise ServiceException(f"Format not allowed. Use: {', '.join(self.__allowed_extensions)}")
        logging.info(f"[{self.__class__.__name__}]: Audio file extension checked.")
        try:
            logging.info(f"[{self.__class__.__name__}]: Saving audio file on the server...")
            recording_path = await self.__file_service.save_recording(file)
            logging.info(f"[{self.__class__.__name__}]: Audio file saved successfully on the server.")
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}]: Failed to save audio file on the server.")
            raise ServiceException(f"Failed to save file to disk: {e}")

        logging.info(f"[{self.__class__.__name__}]: Creating new song with name {name}...")
        new_song = Song(
            sid=-1,
            user_id=user_id,
            name=name,
            genre=genre,
            recording_path=recording_path,
            recording_date=datetime.now(),
            midi_path=None,
            tabs_path=None
        )
        created_song = await self.__repo.create(new_song)
        if not created_song:
            logging.warning(f"[{self.__class__.__name__}]: Failed to create new song with name {name}.")
            self.__file_service.delete_file(recording_path)
            logging.warning(f"[{self.__class__.__name__}]: Rolled back the save of the song's audio file on the server.")
            raise ServiceException("Database error: could not save song record.")
        logging.info(f"[{self.__class__.__name__}]: Successfully created new song with name {name}.")
        return created_song

    async def update_song(self, song_id: int, user_id: int, new_name: str, new_genre: str) -> Song:
        """
        Updates a song with the given id for the user with the given id, from the database, if it exists.
        :param song_id: the id of the song to update
        :param user_id: the id of the user whose song to update
        :param new_name: the new name of the song
        :param new_genre: the new genre of the song
        :return: the updated Song object
        """
        logging.info(f"[{self.__class__.__name__}]: Checking if the new name and genre are not empty...")
        if not new_name or not new_genre:
            logging.warning(f"[{self.__class__.__name__}]: There is no new name or genre provided.")
            raise ServiceException("Name and genre cannot be empty")
        logging.info(f"[{self.__class__.__name__}]: New name and genre check passed.")
        logging.info(f"[{self.__class__.__name__}]: Checking if there is a song with id {song_id} in the database...")
        existing_song = await self.__repo.get_by_id(song_id)
        if not existing_song or existing_song.get_user_id() != user_id:
            logging.warning(f"[{self.__class__.__name__}]: There is no song with id {song_id} in the database.")
            raise ServiceException("Song not found or you don't have permission to edit it.")
        logging.info(f"[{self.__class__.__name__}]: Song found.")
        logging.info(f"[{self.__class__.__name__}]: Updating song with id {song_id}...")
        updated_song_obj = Song(
            sid=existing_song.get_id(),
            user_id=existing_song.get_user_id(),
            name=new_name,
            genre=new_genre,
            recording_path=existing_song.get_recording_path(),
            recording_date=existing_song.get_recording_date(),
            tabs_path=existing_song.get_tabs_path(),
            generated_date=existing_song.get_generated_date(),
            midi_path=existing_song.get_midi_path(),
            midi_date=existing_song.get_midi_date()
        )
        result = await self.__repo.update(updated_song_obj)
        if result is not None:
            logging.warning(f"[{self.__class__.__name__}]: Failed to update song with id {song_id}.")
            raise ServiceException("Failed to update song or no changes detected.")
        logging.info(f"[{self.__class__.__name__}]: Successfully updated song with id {song_id}.")
        return updated_song_obj

    async def delete_song(self, song_id: int, user_id: int) -> None:
        """
        Deletes a song with the given id for the user with given id, from the database, if it exists.
        :param song_id: the id of the song to delete
        :param user_id: the id of the user whose song to delete
        :return: None
        """
        logging.info(f"[{self.__class__.__name__}]: Checking if there is a song with id {song_id} for the user with id {user_id} in the database...")
        existing_song = await self.__repo.get_by_id(song_id)
        if not existing_song or existing_song.get_user_id() != user_id:
            logging.warning(f"[{self.__class__.__name__}]: There is no song with id {song_id} for the user with id {user_id}.")
            raise ServiceException("Song not found or you don't have permission to delete it.")
        logging.info(f"[{self.__class__.__name__}]: Song found.")
        logging.info(f"[{self.__class__.__name__}]: Deleting song with id {song_id}...")
        deleted_song = await self.__repo.delete(song_id)
        if not deleted_song:
            logging.warning(f"[{self.__class__.__name__}]: Failed to delete song with id {song_id}.")
            raise ServiceException("Failed to delete song from database.")
        logging.info(f"[{self.__class__.__name__}]: Successfully deleted song with id {song_id}.")
        try:
            logging.info(f"[{self.__class__.__name__}]: Deleting song recording, MIDI and Tabs files if they exist on the server...")
            if deleted_song.get_recording_path(): self.__file_service.delete_file(deleted_song.get_recording_path())
            if deleted_song.get_midi_path(): self.__file_service.delete_file(str(deleted_song.get_midi_path()))
            if deleted_song.get_tabs_path():
                base_path_without_ext = str(deleted_song.get_tabs_path()).rsplit('.', 1)[0]
                for ext in ['txt', 'pdf', 'docx', 'odt']:
                    try: self.__file_service.delete_file(f"{base_path_without_ext}.{ext}")
                    except Exception as e: logging.warning(f"[{self.__class__.__name__}]: Failed to delete tabs file {base_path_without_ext}: {e}.")
            logging.info(f"[{self.__class__.__name__}]: Song recording, MIDI and Tabs files deleted successfully.")
        except Exception as e: logging.warning(f"[{self.__class__.__name__}]: Failed to delete some files on the server for the song with id {song_id} : {e}.")

    async def trigger_tab_generation(self, song_id: int, user_id: int) -> None:
        """
        Triggers the tab generation for the song with given id of the user with given id.
        :param song_id: the id of the song's tabs generation to trigger
        :param user_id: the id of the song's user to trigger the tab generation for
        :return: None
        """
        try:
            logging.info(f"[{self.__class__.__name__}]: Checking if there exists a song with id {song_id} in the database...")
            song = await self.__repo.get_by_id(song_id)
            if not song or song.get_user_id() != user_id:
                logging.warning(f"[{self.__class__.__name__}]: There is no song with id {song_id}.")
                raise ServiceException("Song not found or unauthorized")
            logging.info(f"[{self.__class__.__name__}]: Song found.")
            audio_path_full = os.path.join(self.__file_service.get_base_songs_dir(), song.get_recording_path().split('songs/')[-1])
            midi_path = song.get_midi_path()

            if not midi_path:
                logging.info(f"[{self.__class__.__name__}]: Triggering MIDI generation for song with id {song_id}")
                midi_full_path = await self.__inference_service.audio_to_midi(
                    audio_file_path=audio_path_full,
                    guitar_model_path="../guitar_model/music",
                    output_dir=self.__file_service.get_midis_dir()
                )
                midi_path = f"midis/{os.path.basename(midi_full_path)}"
                logging.info(f"[{self.__class__.__name__}]: MIDI file created.")

            midi_path_full = os.path.join(self.__file_service.get_base_songs_dir(), midi_path.split('songs/')[-1])
            logging.info(f"[{self.__class__.__name__}]: Triggering Tab generation for song with id {song_id}...")
            tab_full_path = await self.__inference_service.midi_to_tab(
                midi_file_path=midi_path_full,
                output_dir=self.__file_service.get_tabs_dir()
            )
            tab_path = f"tabs/{os.path.basename(tab_full_path)}"
            logging.info(f"[{self.__class__.__name__}]: Tab file created.")
            logging.info(f"[{self.__class__.__name__}]: Updating song data...")
            updated_song = Song(
                sid=song.get_id(),
                user_id=song.get_user_id(),
                name=song.get_name(),
                genre=song.get_genre(),
                recording_path=song.get_recording_path(),
                recording_date=song.get_recording_date(),
                tabs_path=tab_path,
                generated_date=datetime.now(),
                midi_path=midi_path,
                midi_date=datetime.now() if not song.get_midi_path() else song.get_midi_date()
            )
            if await self.__repo.update(updated_song) is not None:
                logging.warning(f"[{self.__class__.__name__}]: Song with id {song_id} update failed. Triggering file save rollback...")
                self.__file_service.delete_file(midi_path_full)
                self.__file_service.delete_file(tab_full_path)
                logging.warning(f"[{self.__class__.__name__}]: File save rolled back successfully.")
                raise ServiceException("Song update failed after tabs generation")
            logging.info(f"[{self.__class__.__name__}]: Song with id {song_id} updated successfully.")
            success_msg = json.dumps({"event": "TAB_READY","song_id": song_id,"song_name": song.get_name()})
            await ws_manager.send_personal_message(success_msg, user_id)
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}]: Failed to trigger the tab generation : {e}.")
            error_msg = json.dumps({"event": "TAB_FAILED","song_id": song_id,"error": repr(e)})
            await ws_manager.send_personal_message(error_msg, user_id)

    async def get_tab_data(self, song_id: int, user_id: int) -> dict:
        """
        Getting tab bytes and song id, name and genre for a song with given id of a user with given id.
        :param song_id: the id for the song for which to get tabs bytes
        :param user_id: the id for the user for which to get a song's tabs bytes
        :return: {"song": {"id": song_id,"name": song_name,"genre": song_genre},"tab_content": tab_bytes} -
        dictionary containing tab bytes and song data
        """
        logging.info(f"[{self.__class__.__name__}]: Finding song with id {song_id} on the server...")
        song = await self.__repo.get_by_id(song_id)
        if not song or song.get_user_id() != user_id:
            logging.error(f"[{self.__class__.__name__}]: Song with id {song_id} not found on server.")
            raise ServiceException("Song not found or unauthorized access.")
        logging.info(f"[{self.__class__.__name__}]: Song with id {song_id} found on server.")
        logging.info(f"[{self.__class__.__name__}]: Checking if the song with id {song_id} has tabs generated on the server...")
        if not song.get_tabs_path():
            logging.error(f"[{self.__class__.__name__}]: Song with id {song_id} has no tabs file on the server.")
            raise ServiceException("Tablature has not been generated for this song.")
        tab_full_path = os.path.join(self.__file_service.get_base_songs_dir(), str(song.get_tabs_path()).split('songs/')[-1])
        if not os.path.exists(tab_full_path):
            logging.error(f"[{self.__class__.__name__}]: Song with id {song_id} has no tabs file on the server.")
            raise ServiceException("Tablature file is missing from the disk.")
        logging.info(f"[{self.__class__.__name__}]: Song with id {song_id} has tabs files on server.")

        try:
            logging.info(f"[{self.__class__.__name__}]: Reading tab bytes from text file...")
            with open(tab_full_path, "r", encoding="utf-8") as f: tab_content = f.read()
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}]: Tablature file reading failed from the disk.")
            raise ServiceException(f"Could not read tab file: {str(e)}")
        logging.info(f"[{self.__class__.__name__}]: Reading tab bytes successful.")
        return {"song": {"id": song.get_id(),"name": song.get_name(),"genre": song.get_genre()},"tab_content": tab_content}

    async def get_download_path(self, song_id: int, user_id: int, file_format: str) -> tuple[str, str, str]:
        """
        Gets the path of the tabs file/ MIDI of a certain song, its filename and corresponding web header file type.
        :param song_id: the id of the song for which to get tabs
        :param user_id: the id of the user whose song's tabs file to be gotten
        :param file_format: the tabs file format or MIDI format
        :return: tuple as it follows: (generated tab_file/MIDI path, tab_file/MIDI filename , web tab_file/MIDI header file type)
        """
        logging.info(f"[{self.__class__.__name__}]: Finding song with id {song_id} on the server...")
        song = await self.__repo.get_by_id(song_id)
        if not song or song.get_user_id() != user_id:
            logging.warning(f"[{self.__class__.__name__}]: Song with id {song_id} not found on server.")
            raise ServiceException("Song not found or unauthorized access.")
        logging.info(f"[{self.__class__.__name__}]: Song found on server.")
        file_format = file_format.lower()
        if file_format in ["midi", "mid"]:
            logging.info(f"[{self.__class__.__name__}]: Getting MIDI file data from the server for song with id {song_id}...")
            if not song.get_midi_path():
                logging.error(f"[{self.__class__.__name__}]: MIDI file not found on the server for song with id {song_id}.")
                raise ServiceException("No MIDI file available.")
            path = os.path.join(self.__file_service.get_base_songs_dir(), str(song.get_midi_path()).split('songs/')[-1])
            if not os.path.exists(path):
                logging.error(f"[{self.__class__.__name__}]: MIDI file not found on the server for song with id {song_id}.")
                raise ServiceException("MIDI file not found on the server.")
            logging.info(f"[{self.__class__.__name__}]: MIDI file found on the server for song with id {song_id}.")
            return path, f"{song.get_name()}.mid", "audio/midi"

        logging.info(f"[{self.__class__.__name__}]: Getting Tabs text file data from the server for song with id {song_id}...")
        if not song.get_tabs_path():
            logging.error(f"[{self.__class__.__name__}]: Tabs text file not found on the server for song with id {song_id}.")
            raise ServiceException("Tablature has not been generated for this song yet.")
        txt_path = os.path.join(self.__file_service.get_base_songs_dir(), str(song.get_tabs_path()).split('songs/')[-1])
        if not os.path.exists(txt_path):
            logging.error(f"[{self.__class__.__name__}]: Tabs text file not found on the server for song with id {song_id}.")
            raise ServiceException("Base text tablature file not found on the server.")
        logging.info(f"[{self.__class__.__name__}]: Tabs text file found on the server for song with id {song_id}.")
        if file_format == "txt":
            logging.info(
                f"[{self.__class__.__name__}]: Tabs .txt file found on the server for song with id {song_id}.")
            return txt_path, f"{song.get_name()}_tab.txt", "text/plain"

        base_dir = os.path.dirname(txt_path)
        base_filename = os.path.splitext(os.path.basename(txt_path))[0]
        generated_file_path = os.path.join(base_dir, f"{base_filename}.{file_format}")

        if not os.path.exists(generated_file_path):
            try:
                with open(txt_path, "r", encoding="utf-8") as f: tab_content = f.read()
                if file_format == "pdf": DocumentGenerator.create_pdf(tab_content, generated_file_path)
                elif file_format == "docx": DocumentGenerator.create_docx(tab_content, generated_file_path)
                elif file_format == "odt": DocumentGenerator.create_odt(tab_content, generated_file_path)
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}]: Unexpected error while getting tabs download path for song with id {song_id}.")
                raise ServiceException(f"Failed to generate .{file_format} file: {str(e)}")

        if not os.path.exists(generated_file_path):
            logging.error(f"[{self.__class__.__name__}]: Tabs text file not found on the server for song with id {song_id}.")
            raise ServiceException(f"Requested .{file_format} file not found on the server.")
        logging.info(f"[{self.__class__.__name__}]: Tabs .{file_format} file found on the server for song with id {song_id}.")
        return generated_file_path, f"{song.get_name()}_tab.{file_format}", self.__mime_types[file_format]
