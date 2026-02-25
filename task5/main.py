from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import  Optional
from enum import Enum

app = FastAPI()


transactions_db = []
next_id = 1


class TransactionType(str, Enum):
    INCOME = "доход"
    EXPENSE = "траты"


class Transaction(BaseModel):
    id: Optional[int] = None
    type: TransactionType
    amount: float
    description: str = ""


@app.post("/transactions/")
def create_transaction(transaction: Transaction):
    global next_id
    

    transaction.id = next_id
    next_id += 1
    
    transactions_db.append(transaction)
    
    return {
        "message": f"добавлена транзакция #{transaction.id}", 
        "transaction": transaction
    }


@app.get("/transactions/")
def get_all_transactions():
    return {"transactions": transactions_db}

@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: int):
    for transaction in transactions_db:
        if transaction.id == transaction_id:
            return transaction
    
    raise HTTPException(status_code=404, detail="транзакция не найдена")

@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, updated_data: Transaction):
    for i, transaction in enumerate(transactions_db):
        if transaction.id == transaction_id:

            updated_data.id = transaction_id
            transactions_db[i] = updated_data
            return {
                "message": f"транзакция #{transaction_id} обновлена",
                "transaction": updated_data
            }
    
    raise HTTPException(status_code=404, detail="транзакция не найдена")

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    for i, transaction in enumerate(transactions_db):
        if transaction.id == transaction_id:
            del transactions_db[i]
            return {"message": f"транзакция #{transaction_id} удалена"}
    
    raise HTTPException(status_code=404, detail="транзакция не найдена")

@app.get("/stats/")
def get_stats():
    total_income = 0
    total_expense = 0
    
    for transaction in transactions_db:
        if transaction.type == TransactionType.INCOME:
            total_income += transaction.amount
        else:
            total_expense += transaction.amount
    
    balance = total_income - total_expense
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }