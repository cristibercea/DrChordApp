from pydantic import BaseModel
class UpdateSongRequest(BaseModel):
    name: str = None
    genre: str = None