from fastapi import HTTPException, Header
from jose import JWTError, jwt
from utils.config_reader import config

async def get_current_user_from_token(token: str) -> int | None:
    try:
        conf = config(section="security")
        secret_key = conf["secret"]
        algorithm = conf["algorithm"]
        if secret_key is None or algorithm is None: raise HTTPException(status_code=501, detail="Internal server error")

        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def extract_user_from_header(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    return await get_current_user_from_token(token)