from pydantic import BaseModel
class RegisterRequest(BaseModel):
    """Register Request model class"""
    name: str
    email: str
    password: str