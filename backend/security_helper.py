from jose import JWTError, jwt
from backend.config_reader import config

def get_current_user_from_token(token: str) -> int | None:
    try:
        conf = config(section="security")
        secret_key = conf["secret"]
        algorithm = conf["algorithm"]
        if secret_key is None or algorithm is None: return None

        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get("sub")
        return None if user_id is None else int(user_id)
    except JWTError:
        return None