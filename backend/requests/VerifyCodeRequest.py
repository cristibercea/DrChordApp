from pydantic import BaseModel
class VerifyCodeRequest(BaseModel):
    email: str
    code: str