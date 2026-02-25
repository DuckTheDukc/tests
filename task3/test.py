import pytest
from fastapi.testclient import TestClient
from main import app, tasks_db  

client = TestClient(app)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_databases():
    tasks_db.clear()
    yield

def test_create_task_and_check_db(client):
    response = client.post("/tasks/", json={"name": "купить молоко", "status": False})
    
    assert response.status_code == 200

    assert "купить молоко" in tasks_db
    assert tasks_db["купить молоко"].name == "купить молоко"
    assert tasks_db["купить молоко"].status == False
    assert len(tasks_db) == 1

def test_create_duplicate_task(client):

    client.post("/tasks/", json={"name": "купить молоко", "status": False})
    

    response = client.post("/tasks/", json={"name": "купить молоко", "status": True})
    
    assert response.status_code == 400

    assert len(tasks_db) == 1
    assert tasks_db["купить молоко"].status == False

def test_get_all_tasks(client):

    tasks_data = [
        {"name": "купить молоко", "status": False},
        {"name": "позвонить маме", "status": True},
        {"name": "сделать зарядку", "status": False}
    ]
    
    for task in tasks_data:
        client.post("/tasks/", json=task)
    
    response = client.get("/tasks/")
    
    assert response.status_code == 200
    assert len(response.json()["tasks"]) == 3

    assert len(tasks_db) == 3
    assert all(name in tasks_db for name in ["купить молоко", "позвонить маме", "сделать зарядку"])

def test_update_task_with_db_check(client):

    client.post("/tasks/", json={"name": "купить молоко", "status": False})
    

    response = client.put("/tasks/купить молоко", 
                         json={"name": "купить хлеб", "status": True})
    
    assert response.status_code == 200
  
    assert "купить молоко" not in tasks_db
    assert "купить хлеб" in tasks_db
    assert tasks_db["купить хлеб"].status == True
    assert len(tasks_db) == 1

def test_delete_task_and_check_db(client):

    client.post("/tasks/", json={"name": "купить молоко", "status": False})
    

    response = client.delete("/tasks/купить молоко")
    
    assert response.status_code == 200

    assert "купить молоко" not in tasks_db
    assert len(tasks_db) == 0

def test_get_nonexistent_task(client):

    assert len(tasks_db) == 0
    
    response = client.get("/tasks/несуществующая задача")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "задача не найдена"

    assert len(tasks_db) == 0