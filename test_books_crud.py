from fastapi import FastAPI
from fastapi.testclient import TestClient
from dotenv import dotenv_values
from pymongo import MongoClient
from routes import router as book_router

app = FastAPI()
config = dotenv_values(".env")
app.include_router(book_router, tags=["books"], prefix="/book")


@app.on_event("startup")
async def startup_event():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"] + "test"]

@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb_client.close()
    app.database.drop_collection("books")

def test_create_book():
    with TestClient(app) as client:
        response = client.post("/book/", json={"title": "Don Quixote", "author": "Miguel de Cervantes", "synopsis": "..."})
        assert response.status_code == 201

        body = response.json()
        assert body.get("title") == "Don Quixote"
        assert body.get("author") == "Miguel de Cervantes"
        assert body.get("synopsis") == "..."
        assert "_id" in body


def test_create_book_missing_title():
    with TestClient(app) as client:
        response = client.post("/book/", json={"author": "Miguel de Cervantes", "synopsis": "..."})
        assert response.status_code == 422


def test_create_book_missing_author():
    with TestClient(app) as client:
        response = client.post("/book/", json={"title": "Don Quixote", "synopsis": "..."})
        assert response.status_code == 422


def test_create_book_missing_synopsis():
    with TestClient(app) as client:
        response = client.post("/book/", json={"title": "Don Quixote", "author": "Miguel de Cervantes"})
        assert response.status_code == 422


def test_get_book():
    with TestClient(app) as client:
        new_book = client.post("/book/", json={"title": "Don Quixote", "author": "Miguel de Cervantes", "synopsis": "..."}).json()

        get_book_response = client.get("/book/" + new_book.get("_id"))
        assert get_book_response.status_code == 200
        assert get_book_response.json() == new_book


def test_get_book_unexisting():
    with TestClient(app) as client:
        get_book_response = client.get("/book/unexisting_id")
        assert get_book_response.status_code == 404


def test_update_book():
    with TestClient(app) as client:
        new_book = client.post("/book/", json={"title": "Don Quixote", "author": "Miguel de Cervantes", "synopsis": "..."}).json()

        response = client.put("/book/" + new_book.get("_id"), json={"title": "Don Quixote 1"})
        assert response.status_code == 200
        assert response.json().get("title") == "Don Quixote 1"


def test_update_book_unexisting():
    with TestClient(app) as client:
        update_book_response = client.put("/book/unexisting_id", json={"title": "Don Quixote 1"})
        assert update_book_response.status_code == 404


def test_delete_book():
    with TestClient(app) as client:
        new_book = client.post("/book/", json={"title": "Don Quixote", "author": "Miguel de Cervantes", "synopsis": "..."}).json()

        delete_book_response = client.delete("/book/" + new_book.get("_id"))
        assert delete_book_response.status_code == 204


def test_delete_book_unexisting():
    with TestClient(app) as client:
        delete_book_response = client.delete("/book/unexisting_id")
        assert delete_book_response.status_code == 404

