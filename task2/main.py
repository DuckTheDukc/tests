from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

books_db = {}

users_db = {}



class Book(BaseModel):
    name: str
    is_available: bool = True
    handler:Optional[str] = None

class User(BaseModel):
    name: str
    books_taken: List[str] = []

@app.post("/books/")
def create_book(book: Book):
    
    if book.name in books_db:
        raise HTTPException(status_code=400, detail= "такая книга уже есть")
    
    books_db[book.name] = book
    return {"message": f"Книга '{book.name}' успешно добавлена","book": book}

@app.put("/books/{book_name}")
def update_book(book_name: str, updated_book:Book):
    if book_name not in books_db:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    if book_name != updated_book.name and updated_book.name in books_db:
        raise HTTPException(status_code=400, detail="Книга с таким названием уже существует")   
    
    old_book = books_db[book_name]
    
    if not old_book.is_available and old_book.handler:
        reader_name = old_book.handler
        if reader_name in users_db:
            reader = users_db[reader_name]
        if book_name in reader.books_taken:
                    reader.books_taken.remove(book_name)
                    reader.books_taken.append(updated_book.name)
                    
    books_db[updated_book.name] = updated_book       
            
    if book_name != updated_book.name:
        del books_db[book_name]

    return {
        "message": f"Книга '{book_name}' обновлена",
    }

@app.get("/books/")
def get_all_books():
    return {"books":list(books_db.values())}
    
    
@app.get("/books/{book_name}")
def get_book(book_name: str):
    if book_name not in books_db:
        raise HTTPException(status_code=404, detail= "Книга не найдена")
    
    return books_db[book_name]



@app.delete("/books/{book_name}")
def delete_book(book_name: str):
    if book_name not in books_db:
        raise HTTPException(status_code=404, detail= "Книга не найдена")
    
    del books_db[book_name]
    return{"message": "книга удалена"}





@app.post ("/users/")
def create_user(user: User):
    
    if user.name in users_db:
        raise HTTPException(status_code=400, detail= "такой пользователь уже есть")
    
    users_db[user.name] = user
    
    return {"user": user}

@app.put("/users/{user_name}")
def update_user(user_name: str, updated_user: User):

    if user_name not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    

    if user_name != updated_user.name and updated_user.name in users_db:
        raise HTTPException(status_code=400, detail="такой пользователь уже есть")
    

    old_user = users_db[user_name]

    updated_user.books_taken = old_user.books_taken.copy()
    

    for book_name in old_user.books_taken:
        if book_name in books_db:
            books_db[book_name].handler = updated_user.name
    

    users_db[updated_user.name] = updated_user
    

    if user_name != updated_user.name:
        del users_db[user_name]
    
    return {
        "message": f"пользователь '{user_name}'  обновлен",

    }

@app.get("/users/")
def get_all_users():
    return {"users":list(users_db.values())}
    
    
@app.get("/users/{user_name}")
def get_user(user_name: str):
    if user_name not in users_db:
        raise HTTPException(status_code=404, detail= "Пользователь не найден")
    
    return users_db[user_name]



@app.delete("/users/{user_name}")
def delete_book(user_name: str):
    if user_name not in users_db:
        raise HTTPException(status_code=404, detail= "Пользователь не найден")
    
    del users_db[user_name]
    return{"message": "пользователь удален"}


@app.post("/borrow/{book_name}/user/{user_name}")
def borrow_book(book_name: str, user_name: str):
    if book_name not in books_db:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    if user_name not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    book = books_db[book_name]
    user = users_db[user_name]
    
    if not book.is_available:
        raise HTTPException(status_code=400, detail="Книга уже взята")
    

    book.is_available = False
    book.handler = user_name
    user.books_taken.append(book_name)
    
    return {
        "message": f"Книга '{book_name}' выдана пользователю '{user_name}'",

    }

@app.post("/return/{book_name}")
def return_book(book_name: str):
    """Читатель возвращает книгу"""
    if book_name not in books_db:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    book = books_db[book_name]
    
    if book.is_available:
        raise HTTPException(status_code=400, detail="Эта не занята")
    
    

    user_name = book.handler
    if user_name in users_db:
        user = users_db[user_name]
        if book_name in user.books_taken:
            user.books_taken.remove(book_name)
    
    book.is_available = True
    book.handler = None
    
    
    return {"message": f"Книга '{book_name}' возвращена"}
