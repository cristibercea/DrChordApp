import logging
from fastapi import FastAPI
from backend.domain.database.DrChordDatabase import DrChordDatabase

logging.basicConfig(filename="target/backend.log", level=logging.INFO)
app = FastAPI()
db = DrChordDatabase()

@app.on_event("startup")
async def startup():
    logging.info("main: Starting up...")
    db.create()

@app.on_event("shutdown")
async def shutdown():
    logging.info("main: Shutting down...")
    await db.disconnect()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
