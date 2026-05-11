import os, json, traceback
from datetime import datetime
from fastapi import UploadFile
from backend.domain.entities.Song import Song
from backend.repository.SongRepository import SongRepository
from backend.service.utils.ServiceException import ServiceException
from backend.service.utils.ConnectionManager import ws_manager
from service.FileService import FileService
from service.InferenceService import InferenceService
from service.utils import DocumentGenerator


class SongService:
    def __init__(self, song_repo: SongRepository):
        self.__repo = song_repo
        self.__file_service = FileService()
        self.__allowed_extensions = ["mp3", "wav", "ogg", "flac"]
        self.__inference_service = InferenceService()
        self.__mime_types = { # Downloaded tabs MIME Types (headers) for the browser
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "odt": "application/vnd.oasis.opendocument.text"
        }

    async def get_user_songs(self, user_id: int, limit: int = 10, offset: int = 0):
        return await self.__repo.get_all_paged_by_user_id(user_id, limit, offset)

    async def get_user_songs_filtered(self, user_id: int, search: str, genre: str, hasTab: str,sortBy: str, limit: int, offset: int):
        return await self.__repo.find_paged_filtered(user_id, search, genre, hasTab, sortBy, limit, offset)

    async def create_song(self, user_id: int, name: str, genre: str, file: UploadFile):
        if not file.filename: raise ServiceException("No file provided")
        ext = file.filename.split('.')[-1].lower()
        if ext not in self.__allowed_extensions: raise ServiceException(f"Format not allowed. Use: {', '.join(self.__allowed_extensions)}")
        try: recording_path = await self.__file_service.save_recording(file)
        except Exception as e: raise ServiceException(f"Failed to save file to disk: {e}")

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
            self.__file_service.delete_file(recording_path)
            raise ServiceException("Database error: could not save song record.")
        return created_song

    async def update_song(self, song_id: int, user_id: int, name: str, genre: str):
        if not name or not genre: raise ServiceException("Name and genre cannot be empty")
        existing_song = await self.__repo.get_by_id(song_id)
        if not existing_song or existing_song.get_user_id() != user_id:
            raise ServiceException("Song not found or you don't have permission to edit it.")

        updated_song_obj = Song(
            sid=existing_song.get_id(),
            user_id=existing_song.get_user_id(),
            name=name,
            genre=genre,
            recording_path=existing_song.get_recording_path(),
            recording_date=existing_song.get_recording_date(),
            tabs_path=existing_song.get_tabs_path(),
            generated_date=existing_song.get_generated_date(),
            midi_path=existing_song.get_midi_path(),
            midi_date=existing_song.get_midi_date()
        )

        result = await self.__repo.update(updated_song_obj)
        if result is not None: raise ServiceException("Failed to update song or no changes detected.")
        return updated_song_obj

    async def delete_song(self, song_id: int, user_id: int): #TODO: test it
        existing_song = await self.__repo.get_by_id(song_id)
        if not existing_song or existing_song.get_user_id() != user_id:
            raise ServiceException("Song not found or you don't have permission to delete it.")
        deleted_song = await self.__repo.delete(song_id)
        if not deleted_song: raise ServiceException("Failed to delete song from database.")
        try:
            if deleted_song.get_recording_path(): self.__file_service.delete_file(deleted_song.get_recording_path())
            if deleted_song.get_midi_path(): self.__file_service.delete_file(str(deleted_song.get_midi_path()))
            if deleted_song.get_tabs_path():
                base_path_without_ext = str(deleted_song.get_tabs_path()).rsplit('.', 1)[0]
                for ext in ['txt', 'pdf', 'docx', 'odt']:
                    try: self.__file_service.delete_file(f"{base_path_without_ext}.{ext}")
                    except Exception: pass
        except Exception as e: print(f"Warning: Could not delete some physical files for song {song_id}: {e}")

        return True

    async def trigger_tab_generation(self, song_id: int, user_id: int):
        try:
            song = await self.__repo.get_by_id(song_id)
            if not song or song.get_user_id() != user_id: raise Exception("Song not found or unauthorized")
            audio_path_full = os.path.join(self.__file_service.BASE_SONGS_DIR,song.get_recording_path().split('songs/')[-1])
            midi_path = song.get_midi_path()

            if not midi_path:
                midi_full_path = await self.__inference_service.audio_to_midi(
                    audio_file_path=audio_path_full,
                    output_dir=self.__file_service.MIDIS_DIR
                )
                midi_path = f"midis/{os.path.basename(midi_full_path)}"

            midi_path_full = os.path.join(self.__file_service.BASE_SONGS_DIR, midi_path.split('songs/')[-1])
            tab_full_path = await self.__inference_service.midi_to_tab(
                midi_file_path=midi_path_full,
                output_dir=self.__file_service.TABS_DIR
            )
            tab_path = f"tabs/{os.path.basename(tab_full_path)}"
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
            if await self.__repo.update(updated_song) is not None: raise ServiceException("Database update failed after generation")
            success_msg = json.dumps({"event": "TAB_READY","song_id": song_id,"song_name": song.get_name()})
            await ws_manager.send_personal_message(success_msg, user_id)
        except Exception as e:
            print(f"\n[CRITIC] EROARE la generarea piesei {song_id}:")
            traceback.print_exc()
            error_msg = json.dumps({"event": "TAB_FAILED","song_id": song_id,"error": repr(e)})
            await ws_manager.send_personal_message(error_msg, user_id)

    async def get_tab_data(self, song_id: int, user_id: int):
        song = await self.__repo.get_by_id(song_id)
        if not song or song.get_user_id() != user_id: raise ServiceException("Song not found or unauthorized access.")
        if not song.get_tabs_path(): raise ServiceException("Tablature has not been generated for this song.")
        tab_full_path = os.path.join(self.__file_service.BASE_SONGS_DIR, str(song.get_tabs_path()).split('songs/')[-1])
        if not os.path.exists(tab_full_path): raise ServiceException("Tablature file is missing from the disk.")

        try:
            with open(tab_full_path, "r", encoding="utf-8") as f: tab_content = f.read()
        except Exception as e: raise ServiceException(f"Could not read tab file: {str(e)}")

        return {
            "song": {
                "id": song.get_id(),
                "name": song.get_name(),
                "genre": song.get_genre()
            },"tab_content": tab_content
        }

    async def get_download_path(self, song_id: int, user_id: int, file_format: str):
        """Returnează calea fizică a fișierului pentru descărcare, generându-l dacă e nevoie."""
        song = await self.__repo.get_by_id(song_id)
        if not song or song.get_user_id() != user_id: raise ServiceException("Song not found or unauthorized access.")
        file_format = file_format.lower()
        if file_format in ["midi", "mid"]:
            if not song.get_midi_path(): raise ServiceException("No MIDI file available.")
            path = os.path.join(self.__file_service.BASE_SONGS_DIR, str(song.get_midi_path()).split('songs/')[-1])
            if not os.path.exists(path): raise ServiceException("MIDI file not found on the server.")
            return path, f"{song.get_name()}.mid", "audio/midi"

        if not song.get_tabs_path(): raise ServiceException("Tablature has not been generated for this song yet.")
        txt_path = os.path.join(self.__file_service.BASE_SONGS_DIR, str(song.get_tabs_path()).split('songs/')[-1])

        if not os.path.exists(txt_path): raise ServiceException("Base text tablature file not found on the server.")
        if file_format == "txt": return txt_path, f"{song.get_name()}_tab.txt", "text/plain"

        base_dir = os.path.dirname(txt_path)
        base_filename = os.path.splitext(os.path.basename(txt_path))[0]
        generated_file_path = os.path.join(base_dir, f"{base_filename}.{file_format}")

        if not os.path.exists(generated_file_path):
            try:
                with open(txt_path, "r", encoding="utf-8") as f: tab_content = f.read()
                if file_format == "pdf": DocumentGenerator.create_pdf(tab_content, generated_file_path)
                elif file_format == "docx": DocumentGenerator.create_docx(tab_content, generated_file_path)
                elif file_format == "odt": DocumentGenerator.create_odt(tab_content, generated_file_path)
            except Exception as e: raise ServiceException(f"Failed to generate .{file_format} file: {str(e)}")

        if not os.path.exists(generated_file_path): raise ServiceException(f"Requested .{file_format} file not found on the server.")
        return generated_file_path, f"{song.get_name()}_tab.{file_format}", self.__mime_types[file_format]
