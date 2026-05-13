import logging, sys, asyncio, random, numpy as np
from datetime import datetime, timedelta
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, File, UploadFile, Form, BackgroundTasks
from backend.domain.database.DrChordDatabase import DrChordDatabase
from backend.repository.UserRepository import UserRepository
from backend.repository.SongRepository import SongRepository
from backend.service.UserService import UserService
from backend.service.SongService import SongService
from backend.service.utils.ConnectionManager import ws_manager
from backend.service.utils.ServiceException import ServiceException
from backend.requests.LoginRequest import LoginRequest
from backend.requests.RegisterRequest import RegisterRequest
from backend.requests.UpdateProfileRequest import UpdateProfileRequest
from backend.requests.UpdateSongRequest import UpdateSongRequest
from backend.requests.VerifyCodeRequest import VerifyCodeRequest
from backend.utils.email_verification_helper import send_verification_code_email
from backend.utils.security_helper import get_current_user_from_token, extract_user_from_header
from service.FileService import FileService

np.seterr(divide="ignore")
if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
logging.basicConfig(filename="target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')

pending_registrations = {}
db = DrChordDatabase("app.ini")
user_repo = UserRepository(db)
song_repo = SongRepository(db)
file_service = FileService()
user_service = UserService(user_repo)
song_service = SongService(song_repo, file_service)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup(): db.create()
@app.on_event("shutdown")
async def shutdown(): await db.disconnect()

@app.post("/auth/login")
async def login(req: LoginRequest):
    try: return await user_service.authenticate_user(req.email, req.password)
    except ServiceException as e: raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/request-signup")
async def request_signup(user_data: RegisterRequest, background_tasks: BackgroundTasks):
    try:
        if await user_service.get_by_email(user_data.email): raise HTTPException(status_code=400, detail="Email already in use.")
        verification_code = str(random.randint(100000, 999999))
        pending_registrations[user_data.email] = {
            "code": verification_code,
            "user_data": user_data,
            "expires_at": datetime.now() + timedelta(minutes=15) # 15 minutes until code expires
        }
        background_tasks.add_task(send_verification_code_email, user_data.email, verification_code)
        return {"message": "Verification code sent! Please check your email."}
    except ServiceException as e: raise HTTPException(status_code=501, detail="Internal server error: " + str(e))

@app.post("/auth/verify-and-register")
async def verify_and_register(data: VerifyCodeRequest):
    pending_user = pending_registrations.get(data.email)
    if not pending_user: raise HTTPException(status_code=404, detail="There is no record for given email.")
    if datetime.now() > pending_user["expires_at"]:
        del pending_registrations[data.email]
        raise HTTPException(status_code=400, detail="Code expired. Please redo the sign up process.")
    if pending_user["code"] != data.code: raise HTTPException(status_code=400, detail="Invalid code.")
    actual_user_data = pending_user["user_data"]
    try:
        await user_service.register_user(actual_user_data.name, actual_user_data.email, actual_user_data.password)
        del pending_registrations[data.email]
        return {"message": "Account verified successfully!"}
    except ServiceException as e: raise HTTPException(status_code=501, detail=str(e))

@app.get("/users/me")
async def get_current_user_profile(user_id: int = Depends(extract_user_from_header)):
    try:
        user = await user_service.get_by_id(user_id)
        if not user: raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.get_id(),"name": user.get_name(),"email": user.get_email()}
    except ServiceException as e: raise HTTPException(status_code=501, detail=str(e))

@app.put("/users/me")
async def update_profile(req: UpdateProfileRequest, user_id: int = Depends(extract_user_from_header)):
    try:
        updated_user_obj = await user_service.update_user(
            user_id=user_id, new_name=req.name, current_password=req.current_password, new_password=req.new_password
        )
        return {"message": "Profile updated successfully","name": updated_user_obj.get_name(),"email": updated_user_obj.get_email()}
    except ServiceException as e: raise HTTPException(status_code=501, detail=str(e))

@app.delete("/users/me")
async def delete_profile(user_id: int = Depends(extract_user_from_header)):
    while True:
        try:
            songs = await song_service.get_user_songs(user_id, limit=1000, offset=0)
            if not songs: break
            for song in songs: await song_service.delete_song(song.get_id(), user_id)
        except ServiceException as e: raise HTTPException(status_code=501, detail="Internal server error: " + str(e))
    try: await user_service.delete_user(user_id)
    except ServiceException as e: raise HTTPException(status_code=501, detail=str(e))
    return {"message": "User account, songs, and all physical files deleted successfully"}

@app.post("/songs/{song_id}/generate-tab")
async def generate_tab(song_id: int, background_tasks: BackgroundTasks, user_id: int = Depends(extract_user_from_header)):
    try:
        background_tasks.add_task(song_service.trigger_tab_generation, song_id, user_id)
        return {"message": "Tab generation started in the background!"}
    except ServiceException as e: raise HTTPException(status_code=501, detail="Internal server error: " + str(e))

@app.post("/songs")
async def upload_song(name: str = Form(...), genre: str = Form(...), file: UploadFile = File(...), user_id: int = Depends(extract_user_from_header)):
    try:
        created_song = await song_service.create_song(user_id, name, genre, file)
        return {
            "message": "Song uploaded successfully",
            "song": {"id": created_song.get_id(), "name": created_song.get_name(), "genre": created_song.get_genre()}
        }
    except ServiceException as e: raise HTTPException(status_code=501, detail=str(e))

@app.put("/songs/{song_id}")
async def update_song(song_id: int, req: UpdateSongRequest, user_id: int = Depends(extract_user_from_header)):
    try:
        await song_service.update_song(song_id, user_id, req.name, req.genre)
        return {"message": "Song updated successfully"}
    except ServiceException as e: raise HTTPException(status_code=501, detail=str(e))

@app.delete("/songs/{song_id}")
async def delete_song(song_id: int, user_id: int = Depends(extract_user_from_header)):
    try:
        await song_service.delete_song(song_id, user_id)
        return {"message": "Song deleted successfully"}
    except ServiceException as e: raise HTTPException(status_code=501, detail=str(e))

@app.get("/songs/{song_id}/tab")
async def get_song_tab(song_id: int, user_id: int = Depends(extract_user_from_header)):
    try: return JSONResponse(status_code=200, content=await song_service.get_tab_data(song_id, user_id))
    except ServiceException as e: raise HTTPException(status_code=404, detail=str(e))
    except Exception as _: raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/songs/{song_id}/download")
async def download_song_file(song_id: int, file_format: str, user_id: int = Depends(extract_user_from_header)):
    try:
        file_path, filename, media_type = await song_service.get_download_path(song_id, user_id, file_format)
        return FileResponse(path=file_path,media_type=media_type,filename=filename)
    except ServiceException as e: raise HTTPException(status_code=400, detail=str(e))
    except Exception as _: raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/songs")
async def get_songs(
        limit: int = Query(10, ge=1),
        offset: int = Query(0, ge=0),
        search: Optional[str] = None,
        genre: Optional[str] = None,
        hasTab: Optional[str] = 'all',
        sortBy: Optional[str] = 'date_desc',
        user_id: int = Depends(extract_user_from_header)
):
    try:
        songs = await song_service.get_user_songs_filtered(user_id, search, genre, hasTab, sortBy, limit, offset)
        return {
            "items": [
                {
                    "id": song.get_id(),
                    "name": song.get_name(),
                    "genre": song.get_genre(),
                    "date_recorded": str(song.get_recording_date()) if song.get_recording_date() else None,
                    "has_tabs": song.get_tabs_path() is not None,
                    "has_midi": song.get_midi_path() is not None
                } for song in songs
            ],"limit": limit,"offset": offset
        }
    except ServiceException as e: raise HTTPException(status_code=501, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try: user_id = await get_current_user_from_token(token)
    except HTTPException: await websocket.close(code=1008); return
    await ws_manager.connect(websocket, user_id)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect: ws_manager.disconnect(user_id)
