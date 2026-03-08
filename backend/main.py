import logging
from fastapi import FastAPI

logging.basicConfig(filename="target/backend.log", level=logging.INFO)
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
