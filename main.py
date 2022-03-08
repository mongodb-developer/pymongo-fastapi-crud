from fastapi import FastAPI
from dotenv import dotenv_values
config = dotenv_values(".env")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


