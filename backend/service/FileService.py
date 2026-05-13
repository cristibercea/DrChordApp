import os, shutil, uuid, logging
from fastapi import UploadFile
from backend.utils.config_reader import config

class FileService:
    """FileService class - responsible with managing files on the server"""
    def __init__(self):
        try:
            song_folder_config = config(section='song_storage_config')
            if song_folder_config['base_songs_dir'] is None or song_folder_config['base_songs_dir'] == '' \
                    or song_folder_config['recordings_dir'] is None or song_folder_config['recordings_dir'] == '' \
                    or song_folder_config['midis_dir'] is None or song_folder_config['midis_dir'] == '' \
                    or song_folder_config['tabs_dir'] is None or song_folder_config['tabs_dir'] == '':
                logging.fatal(f"[{self.__class__.__name__}]: Invalid configuration file!")
                exit(1)
        except FileNotFoundError | RuntimeError as e:
            logging.fatal(e)
            exit(1)

        self.__BASE_SONGS_DIR = str(song_folder_config['base_songs_dir'])
        self.__RECORDINGS_DIR = os.path.join(self.__BASE_SONGS_DIR, str(song_folder_config['recordings_dir']))
        self.__MIDIS_DIR = os.path.join(self.__BASE_SONGS_DIR, str(song_folder_config['midis_dir']))
        self.__TABS_DIR = os.path.join(self.__BASE_SONGS_DIR, str(song_folder_config['tabs_dir']))
        os.makedirs(self.__RECORDINGS_DIR, exist_ok=True)
        os.makedirs(self.__MIDIS_DIR, exist_ok=True)
        os.makedirs(self.__TABS_DIR, exist_ok=True)
        logging.info(f"[{self.__class__.__name__}]: Base songs directory: '{self.__BASE_SONGS_DIR}'; Leaf directories: recording_dir('{self.__RECORDINGS_DIR}'), midi_dir('{self.__MIDIS_DIR}'), tabs_dir('{self.__TABS_DIR}')")

    def get_base_songs_dir(self) -> str: return self.__BASE_SONGS_DIR
    def get_recordings_dir(self) -> str: return self.__RECORDINGS_DIR
    def get_midis_dir(self) -> str: return self.__MIDIS_DIR
    def get_tabs_dir(self) -> str: return self.__TABS_DIR

    async def save_recording(self, file: UploadFile) -> str:
        """
        Save the recording file
        :param file: Upload file object to be saved
        :return: the path of the saved recording file
        """
        logging.info(f"[{self.__class__.__name__}]: Saving recording file '{file.filename}'...")
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'mp3'
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(self.__RECORDINGS_DIR, unique_filename)
        with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        logging.info(f"[{self.__class__.__name__}]: Saved recording file '{file.filename}'.")
        return f"recordings/{unique_filename}"

    def delete_file(self, relative_path: str) -> None:
        """
        Delete the file by its relative path from the server
        :param relative_path: the relative path of the file to be deleted
        :return: None
        """
        logging.info(f"[{self.__class__.__name__}]: Deleting file '{relative_path}'...")
        if not relative_path:
            logging.error(f"[{self.__class__.__name__}]: Empty path!")
            return
        full_path = os.path.join(self.__BASE_SONGS_DIR, relative_path.split('songs/')[-1])
        if os.path.exists(full_path):
            os.remove(full_path)
            logging.info(f"[{self.__class__.__name__}]: Deleted file '{relative_path}'.")
            return
        logging.info(f"[{self.__class__.__name__}]: Failed to delete file '{relative_path}'.")
