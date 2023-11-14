from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from routes import router as book_router

config = dotenv_values(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    yield
    app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(book_router, tags=["books"], prefix="/book")
