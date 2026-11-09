from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from sqlalchemy import create_engine, select, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from datetime import datetime

DB_URL = 'postgresql+psycopg://sd4:sd4@localhost:5432/board'
engine = create_engine(DB_URL)

class Base(DeclarativeBase):
    pass

class Store(Base):
    __tablename__ = 'store_list'    

    store_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    addr: Mapped[str]
    review_list: Mapped[list['Review']] = relationship(back_populates='store')

class Review(Base):
    __tablename__ = 'review_list'

    review_id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[int]
    comment: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    store_id: Mapped[int] = mapped_column(ForeignKey('store_list.store_id'))
    store: Mapped['Store'] = relationship(back_populates='review_list')

app= FastAPI()
templates = Jinja2Templates(directory='templates')

def get_db():
    with Session(engine) as db:
        yield db

def get_store_or_404(store_id: int, db: Session =Depends(get_db)):
    store = db.get(Store, store_id)

    if store is None:
        raise HTTPException(status_code=404, detail='해당 상점이 없습니다.')

    return store

@app.get('/stores')
def store_list(request:Request, db: Session = Depends(get_db)):
    food_store_list = db.execute(
        select(
            Store.store_id, Store.name, Store.addr,
            func.count(Review.review_id).label('review_count'),
            func.coalesce(func.round(func.avg(Review.score), 1), 0).label('avg_score'),
        )
        .outerjoin(Review, Review.store_id == Store.store_id)
        .group_by(Store.store_id)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name='store_list.html',
        context={ 'food_store_list': food_store_list }
    )

@app.get('/stores/{store_id}')
def store_detail(request:Request, food_store: Store = Depends(get_store_or_404)):
    review_list = food_store.review_list
    review_count = len(review_list)
    avg_score = 0 if review_count == 0 else round(sum([review.score for review in review_list]) / review_count, 1)

    return templates.TemplateResponse(
        request=request,
        name='store_detail.html',
        context={
            'food_store': food_store,
            'avg_score': avg_score,
            'review_count': review_count,
            'review_list': sorted(review_list, key=lambda r: r.created_at, reverse=True)
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
def review_create(store_id: int, score: int = Form(), comment: str = Form(), db: Session = Depends(get_db)):
    review = Review(score=score, comment=comment, store_id=store_id)
    db.add(review)
    db.commit()
    return RedirectResponse(f'/stores/{store_id}', status_code=303)

@app.get('/stores/{store_id}/review/{review_id}/edit')
def review_edit(request:Request, store_id: int, review_id: int, db: Session = Depends(get_db)):
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
def review_update(store_id: int, review_id: int, score: int = Form(), comment: str = Form(), db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    review.score = score
    review.comment = comment
    db.commit()
    return RedirectResponse(f'/stores/{store_id}', status_code=303)

@app.post('/stores/{store_id}/review/{review_id}/delete')
def review_delete(store_id: int, review_id: int, db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    db.delete(review)
    db.commit()
    return RedirectResponse(f'/stores/{store_id}', status_code=303)
