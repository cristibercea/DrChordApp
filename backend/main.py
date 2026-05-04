import logging
from fastapi import FastAPI
from backend.domain.database.DrChordDatabase import DrChordDatabase
from backend.domain.entities.Song import Song
from backend.domain.entities.User import User

logging.basicConfig(filename="target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')
db = DrChordDatabase()
app = FastAPI()


@app.on_event("startup")
async def startup():
    logging.info("main: Starting up...")
    db.create()

@app.on_event("shutdown")
async def shutdown():
    logging.info("main: Shutting down...")
    await db.disconnect()

@app.get("/drchord")
async def root():
    return {"message": "Hello World"}

@app.post("/drchord/auth/signin")
async def sign_in(username: str, password: str):
    return {"message": f"Hello"}

@app.post("/drchord/auth/signup")
async def sign_up(user: User):
    return {"message": f"Hello"}

@app.put("/drchord/user?id={user_id}")
async def update_user_profile(user_id: int):
    return {"message": f"Hello"}

@app.delete("/drchord/user=?{user_id}")
async def delete_user_profile(user_id: int):
    return {"message": f"Hello"}

@app.get("/drchord/user/songs?u={user_id}&l={limit}&o={offset}")
async def get_user_songs(user_id: int, limit: int, offset: int):
    return {"message": f"Hello"}

@app.post("/drchord/user/song")
async def create_user_song(song: Song):
    return {"message": f"Hello"}
