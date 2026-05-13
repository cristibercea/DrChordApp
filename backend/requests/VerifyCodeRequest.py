from pydantic import BaseModel
class VerifyCodeRequest(BaseModel):
    """Verify Account Code Request model class"""
    email: str
    code: str