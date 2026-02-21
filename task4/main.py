from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app=FastAPI()

posts_db={}

class post(BaseModel):
    name: str
    text: str
    comments: List[str] = []

@app.post("/posts/")
def create_post(post:post):
    if post.name in posts_db:
        raise HTTPException(status_code=code, detail=detail)
    posts_db[post.name] = post
    return {"message":f"добавлен пост {post.name}", "post":post}

@app.put("/posts/{post_name}")
def update_post(post_name:str, updated_post:post | None = None):
    if post_name not in posts_db:
        raise HTTPException(status_code=404, detail="пост не найден")
    
    if post_name != updated_post.name and updated_post.name in posts_db:
        raise HTTPException(status_code=400, detail="пост с таким названием уже существует") 

    return {"message":"пост обновлен", "post": post}

@app.get("/posts/{post_name}")
def get_post(post_name:str):
    if post_name not in posts_db:
        raise HTTPException(status_code=code, detail=detail)
    return posts_db[post_name]

@app.get("/posts/")
def get_all_posts():
    return {"posts": list(posts_db.values())}

@app.delete("/posts/{post_name}")
def delete_post(post_name:str):
    if post_name not in posts_db:
        raise HTTPException(status_code=code, detail=detail)
    del posts_db[post_name]
    return {"message":"задача удалена"}