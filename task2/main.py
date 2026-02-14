from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()



class Book(BaseModel):
    name: str
    handler: str | None=None

class User(BaseModel):
    name: str
    book_name: str | None=None

@app.post("/books/")
def create_book(book: Book):
    return {"book": book}

@app.post ("/users/")
def create_user(user: User):
    return {"user": user}

@app.get("/books/{book_name}")
def read_book()




