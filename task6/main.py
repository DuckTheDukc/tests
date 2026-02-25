from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


ads_db = {}

class Ad(BaseModel):
    title: str = ""
    description: str = ""
    price: float = 0.0
    seller_name: str = ""

class Review(BaseModel):
    user_name: str = ""
    rating: int = 0
    comment: str = ""

reviews_db = {}  



@app.post("/ads/")
def create_ad(ad: Ad):
    if ad.title in ads_db:
        raise HTTPException(status_code=400, detail="объявление с таким названием уже существует")
    
    if ad.price <= 0:
        raise HTTPException(status_code=400, detail="цена должна быть больше 0")
    
    ads_db[ad.title] = ad
    reviews_db[ad.title] = []  
    
    return {"message": f"добавлено объявление {ad.title}", "ad": ad}

@app.get("/ads/")
def get_all_ads():

    result = []
    for title, ad in ads_db.items():
        reviews = reviews_db.get(title, [])
        

        avg_rating = 0
        if reviews:
            total = 0
            for r in reviews:
                total += r.rating
            avg_rating = total / len(reviews)
        
        result.append({
            "ad": ad,
            "reviews_count": len(reviews),
            "average_rating": round(avg_rating, 1)
        })
    
    return {"ads": result}

@app.get("/ads/{ad_title}")
def get_ad(ad_title: str):
    if ad_title not in ads_db:
        raise HTTPException(status_code=404, detail="объявление не найдено")
    
    ad = ads_db[ad_title]
    reviews = reviews_db.get(ad_title, [])

    avg_rating = 0
    if reviews:
        total = 0
        for r in reviews:
            total += r.rating
        avg_rating = total / len(reviews)
    
    return {
        "ad": ad,
        "reviews": reviews,
        "reviews_count": len(reviews),
        "average_rating": round(avg_rating, 1)
    }

@app.put("/ads/{ad_title}")
def update_ad(ad_title: str, updated_ad: Ad):
    if ad_title not in ads_db:
        raise HTTPException(status_code=404, detail="объявление не найдено")
    

    if ad_title != updated_ad.title and updated_ad.title in ads_db:
        raise HTTPException(status_code=400, detail="объявление с таким названием уже существует")
    

    if ad_title != updated_ad.title:
        reviews_db[updated_ad.title] = reviews_db.pop(ad_title)
        del ads_db[ad_title]
    
    ads_db[updated_ad.title] = updated_ad
    
    return {"message": "объявление обновлено", "ad": updated_ad}

@app.delete("/ads/{ad_title}")
def delete_ad(ad_title: str):
    if ad_title not in ads_db:
        raise HTTPException(status_code=404, detail="объявление не найдено")
 
    del ads_db[ad_title]
    if ad_title in reviews_db:
        del reviews_db[ad_title]
    
    return {"message": "объявление удалено"}



@app.post("/ads/{ad_title}/reviews/")
def create_review(ad_title: str, review: Review):
    if ad_title not in ads_db:
        raise HTTPException(status_code=404, detail="объявление не найдено")
    
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="рейтинг должен быть от 1 до 5")
    
    if not review.comment:
        raise HTTPException(status_code=400, detail="комментарий не может быть пустым")
    
    reviews_db[ad_title].append(review)
    
    return {"message": "отзыв добавлен", "review": review}

@app.get("/ads/{ad_title}/reviews/")
def get_reviews(ad_title: str):
    if ad_title not in ads_db:
        raise HTTPException(status_code=404, detail="объявление не найдено")
    
    return {
        "ad_title": ad_title,
        "reviews": reviews_db.get(ad_title, [])
    }

@app.delete("/reviews/{ad_title}/{review_index}")
def delete_review(ad_title: str, review_index: int):
    if ad_title not in ads_db:
        raise HTTPException(status_code=404, detail="объявление не найдено")
    
    reviews = reviews_db.get(ad_title, [])
    
    if review_index < 0 or review_index >= len(reviews):
        raise HTTPException(status_code=404, detail="отзыв не найден")
    
    deleted_review = reviews.pop(review_index)
    
    return {"message": "отзыв удален", "review": deleted_review}