import pytest
from fastapi.testclient import TestClient
import main
from main import app, transactions_db

client = TestClient(app)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_databases():
    transactions_db.clear()
    main.next_id = 1
    yield
    
def test_create_transaction_and_check_db(client):

    response = client.post("/transactions/", json={
        "type": "доход",
        "amount": 5000.50,
        "description": "зарплата"
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "добавлена транзакция #1"

    assert len(transactions_db) == 1
    transaction = transactions_db[0]
    assert transaction.id == 1
    assert transaction.type == "доход"
    assert transaction.amount == 5000.50
    assert transaction.description == "зарплата"

def test_create_multiple_transactions_check_ids(client):

    response1 = client.post("/transactions/", json={
        "type": "доход",
        "amount": 10000,
        "description": "зарплата"
    })
    assert response1.json()["message"] == "добавлена транзакция #1"

    response2 = client.post("/transactions/", json={
        "type": "траты",
        "amount": 1500.75,
        "description": "продукты"
    })
    assert response2.status_code == 200
    assert response2.json()["message"] == "добавлена транзакция #2"
    
    response3 = client.post("/transactions/", json={
        "type": "траты",
        "amount": 500,
        "description": "такси"
    })
    assert response3.status_code == 200
    assert response3.json()["message"] == "добавлена транзакция #3"

    assert len(transactions_db) == 3
    assert transactions_db[0].id == 1
    assert transactions_db[1].id == 2
    assert transactions_db[2].id == 3

def test_get_transaction_by_id(client):

    client.post("/transactions/", json={"type": "доход", "amount": 10000, "description": "зарплата"})
    client.post("/transactions/", json={"type": "траты", "amount": 500, "description": "кофе"})
    client.post("/transactions/", json={"type": "доход", "amount": 2000, "description": "фриланс"})

    response = client.get("/transactions/2")
    
    assert response.status_code == 200
    transaction = response.json()
    assert transaction["id"] == 2
    assert transaction["type"] == "траты"
    assert transaction["amount"] == 500
    assert transaction["description"] == "кофе"

    assert transactions_db[1].id == 2
    assert transactions_db[1].amount == 500

def test_update_transaction(client):

    client.post("/transactions/", json={
        "type": "траты",
        "amount": 1000,
        "description": "ресторан"
    })

    response = client.put("/transactions/1", json={
        "type": "траты",
        "amount": 1500,
        "description": "ресторан с друзьями"
    })
    
    assert response.status_code == 200
    assert response.json()["message"] == "транзакция #1 обновлена"

    assert len(transactions_db) == 1
    updated = transactions_db[0]
    assert updated.id == 1
    assert updated.amount == 1500
    assert updated.description == "ресторан с друзьями"

def test_delete_transaction(client):

    client.post("/transactions/", json={"type": "доход", "amount": 50000, "description": "зарплата"})
    client.post("/transactions/", json={"type": "траты", "amount": 3000, "description": "аренда"})
    client.post("/transactions/", json={"type": "траты", "amount": 1000, "description": "интернет"})
    
    assert len(transactions_db) == 3
    
    response = client.delete("/transactions/2")
    
    assert response.status_code == 200
    assert response.json()["message"] == "транзакция #2 удалена"
    
    assert len(transactions_db) == 2
    assert transactions_db[0].id == 1
    assert transactions_db[1].id == 3
    
    get_response = client.get("/transactions/2")
    assert get_response.status_code == 404

def test_get_stats(client):

    transactions = [
        {"type": "доход", "amount": 50000, "description": "зарплата"},
        {"type": "траты", "amount": 15000, "description": "аренда"},
        {"type": "доход", "amount": 3000, "description": "фриланс"},
        {"type": "траты", "amount": 2000, "description": "продукты"},
        {"type": "траты", "amount": 1000, "description": "интернет"}
    ]
    
    for t in transactions:
        client.post("/transactions/", json=t)

    assert len(transactions_db) == 5
    
    response = client.get("/stats/")
    
    assert response.status_code == 200
    stats = response.json()
    
    assert stats["total_income"] == 53000  
    assert stats["total_expense"] == 18000  
    assert stats["balance"] == 35000 
    

    client.post("/transactions/", json={"type": "доход", "amount": 10000, "description": "премия"})
    
    response2 = client.get("/stats/")
    assert response2.json()["total_income"] == 63000
    assert response2.json()["balance"] == 45000