from fastapi import FastAPI, HTTPException, Path, Query, Body, Depends
from pydantic import BaseModel
from typing import Dict
import pytest
from fastapi.testclient import TestClient

app = FastAPI()

# Імпровізована база даних - словник для зберігання постів
db_posts = {
    1: {"title": "Перший пост", "content": "Це контент першого поста."},
    2: {"title": "Другий пост", "content": "Це контент другого поста."}
}

# Лічильники для статистики
stats = {
    "version": {"GET": 0},
    "posts": {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0},
    "stats": {"GET": 0}
}

client = TestClient(app)


class Post(BaseModel):
    title: str
    content: str


@app.get("/version")
def version():
    stats["version"]["GET"] += 1
    return {"version": "1.0.0"}


@app.get("/posts")
def get_posts():
    stats["posts"]["GET"] += 1
    return db_posts


@app.post("/posts")
def create_post(post: Post):
    stats["posts"]["POST"] += 1
    post_id = max(db_posts.keys()) + 1
    db_posts[post_id] = post.dict()
    return {"message": "Post created successfully", "post_id": post_id}


@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
    stats["posts"]["PUT"] += 1
    if post_id not in db_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    db_posts[post_id] = post.dict()
    return {"message": "Post updated successfully", "post_id": post_id}


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    stats["posts"]["DELETE"] += 1
    if post_id not in db_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    del db_posts[post_id]
    return {"message": "Post deleted successfully", "post_id": post_id}


@app.get("/stats")
def get_stats():
    stats["stats"]["GET"] += 1
    return stats


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}


def test_get_posts():
    response = client.get("/posts")
    assert response.status_code == 200
    assert len(response.json()) == 2  # Перевіряємо початкову кількість постів


def test_create_post():
    data = {"title": "Третій пост", "content": "Це контент третього поста."}
    response = client.post("/posts", json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "Post created successfully"


def test_update_post():
    data = {"title": "Оновлений пост", "content": "Це оновлений контент поста."}
    response = client.put("/posts/1", json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "Post updated successfully"


def test_delete_post():
    response = client.delete("/posts/2")
    assert response.status_code == 200
    assert response.json()["message"] == "Post deleted successfully"


def test_get_stats():
    response = client.get("/stats")
    assert response.status_code == 200
    assert "version" in response.json()
    assert "posts" in response.json()
    assert "stats" in response.json()


def test_update_non_existing_post():
    data = {"title": "Оновлений пост", "content": "Це оновлений контент поста."}
    response = client.put("/posts/1000", json=data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_delete_non_existing_post():
    response = client.delete("/posts/1000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"