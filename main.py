from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

DB_URL = 'postgresql+psycopg://sd4:sd4@localhost:5432/board'
engine = create_engine(DB_URL)

class Base(DeclarativeBase):
    pass

class Store(Base):
    __tablename__ = 'store_list'    

    store_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    addr: Mapped[str]

class Review(Base):
    __tablename__ = 'review_list'

    review_id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[int]
    comment: Mapped[str]
    store_id: Mapped[int]

app= FastAPI()
templates = Jinja2Templates(directory='templates')

@app.get('/stores')
def store_list(request:Request):
    with Session(engine) as db:
        food_store_list = db.scalars(select(Store)).all()

        review_counts = {}
        for food_store in food_store_list:
            review_list = db.scalars(select(Review).where(Review.store_id == food_store.store_id)).all()
            review_counts[food_store.store_id] = len(review_list)

        return templates.TemplateResponse(
            request=request,
            name='store_list.html',
            context={ 'food_store_list': food_store_list, 'review_counts': review_counts }
        )

@app.get('/stores/{store_id}')
def store_detail(request:Request, store_id: int):
    with Session(engine) as db:
        food_store = db.get(Store, store_id)
        review_list = db.scalars(select(Review).where(Review.store_id == store_id)).all()
        review_count = len(review_list)
        avg_score = 0 if review_count == 0 else round(sum([review.score for review in review_list]) / review_count, 1)
    
        return templates.TemplateResponse(
            request=request,
            name='store_detail.html',
            context={ 
                'food_store': food_store,
                'avg_score': avg_score,
                'review_count': review_count,
                'review_list': review_list
            }
        )

@app.get('/stores/{store_id}/review/new')
def review_new(request:Request, store_id: int):
    return templates.TemplateResponse(
        request=request,
        name='review_new.html',
        context={ 'store_id': store_id }
    )    

@app.post('/stores/{store_id}/review/create')
def review_create(store_id: int, score: int = Form(), comment: str = Form()):
    with Session(engine) as db:
        review = Review(score=score, comment=comment, store_id=store_id)
        db.add(review)
        db.commit()
    return RedirectResponse(f'/stores/{store_id}', status_code=303)

@app.get('/stores/{store_id}/review/{review_id}/edit')
def review_edit(request:Request, store_id: int, review_id: int):
    with Session(engine) as db:
        review = db.get(Review, review_id)
    
        return templates.TemplateResponse(
            request=request,
            name='review_edit.html',
            context={
                'store_id': store_id, 
                'review_id': review_id,
                'review': review,
            }
    )  

@app.post('/stores/{store_id}/review/{review_id}/update')
def review_update(store_id: int, review_id: int, score: int = Form(), comment: str = Form()):
    with Session(engine) as db:
        review = db.get(Review, review_id)
        review.score = score
        review.comment = comment
        db.commit()
    return RedirectResponse(f'/stores/{store_id}', status_code=303)

@app.get('/stores/{store_id}/review/{review_id}/delete')
def review_delete(store_id: int, review_id: int):
    with Session(engine) as db:
        review = db.get(Review, review_id)
        db.delete(review)
        db.commit()
    return RedirectResponse(f'/stores/{store_id}', status_code=303)
