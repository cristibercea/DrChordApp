import os, shutil, uuid
from fastapi import UploadFile

class FileService:
    def __init__(self):
        self.BASE_SONGS_DIR = "songs"
        self.RECORDINGS_DIR = os.path.join(self.BASE_SONGS_DIR, "recordings")
        self.MIDIS_DIR = os.path.join(self.BASE_SONGS_DIR, "midis")
        self.TABS_DIR = os.path.join(self.BASE_SONGS_DIR, "tabs")
        os.makedirs(self.RECORDINGS_DIR, exist_ok=True)
        os.makedirs(self.MIDIS_DIR, exist_ok=True)
        os.makedirs(self.TABS_DIR, exist_ok=True)

    async def save_recording(self, file: UploadFile) -> str:
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'mp3'
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(self.RECORDINGS_DIR, unique_filename)
        with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        return f"recordings/{unique_filename}"

    def delete_file(self, relative_path: str):
        if not relative_path: return
        full_path = os.path.join(self.BASE_SONGS_DIR, relative_path.split('songs/')[-1])
        if os.path.exists(full_path): os.remove(full_path)
