import logging
from jose import JWTError, jwt
from fastapi import HTTPException, Header
from backend.utils.config_reader import config

async def get_current_user_from_token(token: str) -> int | None:
    logging.info(f"Getting user id from token {token}...")
    try:
        conf = config(section="security")
        secret_key = conf["secret"]
        algorithm = conf["algorithm"]
        if secret_key is None or algorithm is None:
            logging.error(f"Failed to get user id from token {token}.")
            raise HTTPException(status_code=501, detail="Internal server error")

        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        logging.info(f"User id from token {token} is {payload['sub']}.")
        return int(payload.get("sub"))
    except JWTError:
        logging.error(f"Failed to get user id from token {token}.")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except FileNotFoundError | RuntimeError as e:
        logging.fatal(e)
        raise HTTPException(status_code=501, detail="Internal server error: "+e)

async def extract_user_from_header(authorization: str = Header(None)):
    logging.info(f"Getting user id from header...")
    if not authorization or not authorization.startswith("Bearer "):
        logging.error(f"Failed to get user id from header: {authorization}")
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    return await get_current_user_from_token(token)