from pydantic import BaseModel
from typing import Optional
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None