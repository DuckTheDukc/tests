from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app=FastAPI()

tasks_db={}

class task(BaseModel):
    name:str = ""
    status: bool = False

@app.post("/tasks/")
def create_task(task:task):
    if task.name in tasks_db:
        raise HTTPException(status_code=code, detail=detail)
    tasks_db[task.name] = task
    return {"message":f"добавлена задача {task.name}", "task":task}

@app.put("/tasks/{task_name}")
def update_task(task_name:str, updated_task:task | None = None):
    if task_name not in tasks_db:
        raise HTTPException(status_code=404, detail="задача не найдена")
    
    if task_name != updated_task.name and updated_task.name in tasks_db:
        raise HTTPException(status_code=400, detail="задача с таким названием уже существует") 

    return {"message":"задача обновлена", "task": task}

@app.get("/tasks/{task_name}")
def get_task(task_name:str):
    if task_name not in tasks_db:
        raise HTTPException(status_code=code, detail=detail)
    return tasks_db[task_name]

@app.get("/tasks/")
def get_all_tasks():
    return {"tasks": list(tasks_db.values())}

@app.delete("/tasks/{task_name}")
def delete_task(task_name:str):
    if task_name not in tasks_db:
        raise HTTPException(status_code=code, detail=detail)
    del tasks_db[task_name]
    return {"message":"задача удалена"}