from pydantic import BaseModel
from typing import Optional
class UpdateProfileRequest(BaseModel):
    """Update Profile Request model class"""
    name: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None