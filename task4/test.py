import pytest
from fastapi.testclient import TestClient
from main import app, posts_db 

client = TestClient(app)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_databases():
    posts_db.clear()
    yield

def test_create_post_and_check_db(client):

    response = client.post("/posts/", json={
        "name": "моя первая запись",
        "text": "сегодня отличный день",
        "comments": ["класс!", "согласен"]
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "добавлен пост моя первая запись"
    
    assert "моя первая запись" in posts_db
    post = posts_db["моя первая запись"]
    assert post.name == "моя первая запись"
    assert post.text == "сегодня отличный день"
    assert post.comments == ["класс!", "согласен"]
    assert len(posts_db) == 1

def test_create_duplicate_post(client):

    client.post("/posts/", json={
        "name": "моя первая запись",
        "text": "сегодня отличный день",
        "comments": []
    })
    
    response = client.post("/posts/", json={
        "name": "моя первая запись",
        "text": "другой текст",
        "comments": ["комментарий"]
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == "пост с таким названием уже существует"

    assert len(posts_db) == 1
    assert posts_db["моя первая запись"].text == "сегодня отличный день"
    assert posts_db["моя первая запись"].comments == []

def test_get_all_posts(client):

    posts_data = [
        {"name": "пост 1", "text": "текст 1", "comments": ["комм1"]},
        {"name": "пост 2", "text": "текст 2", "comments": []},
        {"name": "пост 3", "text": "текст 3", "comments": ["комм2", "комм3"]}
    ]
    
    for post in posts_data:
        client.post("/posts/", json=post)
    
    response = client.get("/posts/")
    
    assert response.status_code == 200
    posts = response.json()["posts"]
    assert len(posts) == 3
    
    assert len(posts_db) == 3
    assert "пост 1" in posts_db
    assert "пост 2" in posts_db
    assert "пост 3" in posts_db
    assert posts_db["пост 2"].comments == []


def test_update_post_preserve_comments(client):

    client.post("/posts/", json={
        "name": "интересный пост",
        "text": "начальный текст",
        "comments": ["комм1", "комм2"]
    })
    
    response = client.put("/posts/интересный пост", json={
        "name": "интересный пост",
        "text": "обновленный текст",
        "comments": ["комм1", "комм2"]
    })
    
    assert response.status_code == 200
    
    assert posts_db["интересный пост"].comments == ["комм1", "комм2"]
    assert posts_db["интересный пост"].text == "обновленный текст"

def test_delete_post_with_comments(client):

    client.post("/posts/", json={
        "name": "пост для удаления",
        "text": "какой-то текст",
        "comments": ["комм1", "комм2", "комм3"]
    })
    
    assert "пост для удаления" in posts_db
    assert len(posts_db["пост для удаления"].comments) == 3
    
    response = client.delete("/posts/пост для удаления")
    
    assert response.status_code == 200
    assert response.json()["message"] == "пост удален"
    
    assert "пост для удаления" not in posts_db
    assert len(posts_db) == 0