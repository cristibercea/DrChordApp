from pydantic import BaseModel
class LoginRequest(BaseModel):
    """Login Request model class"""
    email: str
    password: str