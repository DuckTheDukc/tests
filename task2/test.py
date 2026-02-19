import pytest
from fastapi.testclient import TestClient
from main import app, books_db, users_db 


@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_databases():
    books_db.clear()
    users_db.clear()
    yield

def test_create_and_duplicate_book(client):
    response = client.post("/books/", json={"name": "Война и мир", "is_available": True, "handler": None})
    assert response.status_code == 200
    assert response.json()["book"]["name"] == "Война и мир"
    assert "Война и мир" in books_db
    response_duplicate = client.post("/books/", json={"name": "Война и мир", "is_available": True, "handler": None})
    assert response_duplicate.status_code == 400
    assert response_duplicate.json()["detail"] == "такая книга уже есть"
    assert len(books_db) == 1

def test_borrow_and_return_book(client):
    client.post("/books/", json={"name": "Преступление и наказание", "is_available": True})
    client.post("/users/", json={"name": "Иван", "books_taken": []})
    borrow_response = client.post("/borrow/Преступление и наказание/user/Иван")
    assert borrow_response.status_code == 200
    assert borrow_response.json()["message"] == "Книга 'Преступление и наказание' выдана пользователю 'Иван'"
    book = books_db["Преступление и наказание"]
    user = users_db["Иван"]
    assert book.is_available is False         
    assert book.handler == "Иван"              
    assert "Преступление и наказание" in user.books_taken  
    return_response = client.post("/return/Преступление и наказание")
    assert return_response.status_code == 200
    assert return_response.json()["message"] == "Книга 'Преступление и наказание' возвращена"
    book = books_db["Преступление и наказание"]
    user = users_db["Иван"]
    assert book.is_available is True          
    assert book.handler is None                 
    assert "Преступление и наказание" not in user.books_taken  

def test_update_book_with_rename_while_borrowed(client):
    client.post("/books/", json={"name": "СтароеНазвание"})
    client.post("/users/", json={"name": "Иван"})
    client.post("/borrow/СтароеНазвание/user/Иван")
    response = client.put("/books/СтароеНазвание", json={"name": "НовоеНазвание", "is_available": False, "handler": "Иван"})
    assert response.status_code == 200
    assert "СтароеНазвание" not in books_db
    assert "НовоеНазвание" in books_db
    assert books_db["НовоеНазвание"].handler == "Иван"
    assert "НовоеНазвание" in users_db["Иван"].books_taken
    assert "СтароеНазвание" not in users_db["Иван"].books_taken

def test_update_user_with_rename_while_having_books(client):
    client.post("/books/", json={"name": "название"})
    client.post("/users/", json={"name": "Иван"})
    client.post("/borrow/название/user/Иван")
    updated_user_data = {"name": "Иван Иванов", "books_taken": []} 
    response = client.put("/users/Иван", json=updated_user_data)
    assert response.status_code == 200
    assert "Иван" not in users_db
    assert "Иван Иванов" in users_db
    assert books_db["название"].handler == "Иван Иванов"
    assert "название" in users_db["Иван Иванов"].books_taken


def test_borrow_already_taken_book(client):
    client.post("/books/", json={"name": "РедкаяКнига"})
    client.post("/users/", json={"name": "Макс"})
    client.post("/users/", json={"name": "Иван"})
    client.post("/borrow/РедкаяКнига/user/Макс")
    response = client.post("/borrow/РедкаяКнига/user/Иван")
    assert response.status_code == 400
    assert response.json()["detail"] == "Книга уже взята"
    assert "РедкаяКнига" not in users_db["Иван"].books_taken