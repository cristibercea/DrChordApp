from pydantic import BaseModel
class UpdateSongRequest(BaseModel):
    """Update Song Request model class"""
    name: str = None
    genre: str = None