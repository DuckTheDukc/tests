import pytest
from fastapi.testclient import TestClient
from main import app, ads_db, reviews_db

client = TestClient(app)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_databases():
    ads_db.clear()
    reviews_db.clear()
    yield

def test_create_ad_and_check_db(client):

    response = client.post("/ads/", json={
        "title": "Продам ноутбук",
        "description": "Игровой ноутбук, состояние отличное",
        "price": 50000.0,
        "seller_name": "Иван Петров"
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "добавлено объявление Продам ноутбук"
    
    assert "Продам ноутбук" in ads_db
    ad = ads_db["Продам ноутбук"]
    assert ad.title == "Продам ноутбук"
    assert ad.price == 50000.0
    assert ad.seller_name == "Иван Петров"
    
    assert "Продам ноутбук" in reviews_db
    assert reviews_db["Продам ноутбук"] == []

def test_create_ad_with_invalid_price(client):

    response1 = client.post("/ads/", json={
        "title": "Ноутбук",
        "description": "Описание",
        "price": 0,
        "seller_name": "Иван"
    })
    
    assert response1.status_code == 400
    assert response1.json()["detail"] == "цена должна быть больше 0"

    response2 = client.post("/ads/", json={
        "title": "Телефон",
        "description": "Описание",
        "price": -1000,
        "seller_name": "Петр"
    })
    
    assert response2.status_code == 400

    assert len(ads_db) == 0
    assert len(reviews_db) == 0

def test_create_review_for_ad(client):


    client.post("/ads/", json={
        "title": "Квартира",
        "description": "Сдается квартира",
        "price": 30000.0,
        "seller_name": "Агентство"
    })
    

    response = client.post("/ads/Квартира/reviews/", json={
        "user_name": "Алексей",
        "rating": 5,
        "comment": "Отличная квартира, все понравилось"
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "отзыв добавлен"

    assert "Квартира" in reviews_db
    assert len(reviews_db["Квартира"]) == 1
    
    review = reviews_db["Квартира"][0]
    assert review.user_name == "Алексей"
    assert review.rating == 5
    assert review.comment == "Отличная квартира, все понравилось"

    client.post("/ads/Квартира/reviews/", json={
        "user_name": "Мария",
        "rating": 4,
        "comment": "Хорошая квартира, но дороговато"
    })
    
    assert len(reviews_db["Квартира"]) == 2

def test_get_ad_with_reviews_and_rating(client):

    client.post("/ads/", json={
        "title": "Курсы английского",
        "description": "Индивидуальные занятия",
        "price": 2000.0,
        "seller_name": "Анна"
    })

    reviews_data = [
        {"user_name": "Дмитрий", "rating": 5, "comment": "Супер!"},
        {"user_name": "Елена", "rating": 4, "comment": "Хорошо"},
        {"user_name": "Сергей", "rating": 3, "comment": "Нормально"}
    ]
    
    for review in reviews_data:
        client.post("/ads/Курсы английского/reviews/", json=review)

    response = client.get("/ads/Курсы английского")
    
    assert response.status_code == 200
    data = response.json()
    

    assert data["ad"]["title"] == "Курсы английского"
    assert data["ad"]["price"] == 2000.0

    assert data["reviews_count"] == 3
    assert len(data["reviews"]) == 3

    assert data["average_rating"] == 4.0
    
    assert len(reviews_db["Курсы английского"]) == 3

def test_delete_review(client):

    client.post("/ads/", json={
        "title": "Услуги репетитора",
        "description": "Математика",
        "price": 1500.0,
        "seller_name": "Михаил"
    })
    
    for i in range(3):
        client.post("/ads/Услуги репетитора/reviews/", json={
            "user_name": f"User{i}",
            "rating": 5,
            "comment": f"Отзыв {i}"
        })
    
    assert len(reviews_db["Услуги репетитора"]) == 3

    response = client.delete("/reviews/Услуги репетитора/1")
    
    assert response.status_code == 200
    assert response.json()["message"] == "отзыв удален"

    assert len(reviews_db["Услуги репетитора"]) == 2

    remaining_reviews = reviews_db["Услуги репетитора"]
    assert remaining_reviews[0].comment == "Отзыв 0"
    assert remaining_reviews[1].comment == "Отзыв 2"

    response404 = client.delete("/reviews/Услуги репетитора/5")
    assert response404.status_code == 404

def test_delete_ad_with_reviews(client):

    client.post("/ads/", json={
        "title": "Машина",
        "description": "Продам авто",
        "price": 500000.0,
        "seller_name": "Владимир"
    })

    for i in range(3):
        client.post("/ads/Машина/reviews/", json={
            "user_name": f"User{i}",
            "rating": 5,
            "comment": f"Отзыв {i}"
        })
    
    assert "Машина" in ads_db
    assert "Машина" in reviews_db
    assert len(reviews_db["Машина"]) == 3
    
    response = client.delete("/ads/Машина")
    
    assert response.status_code == 200
    assert response.json()["message"] == "объявление удалено"

    assert "Машина" not in ads_db

    assert "Машина" not in reviews_db

    get_response = client.get("/ads/Машина")
    assert get_response.status_code == 404