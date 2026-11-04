from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app= FastAPI()
templates = Jinja2Templates(directory='templates')

food_store_list = [
    {
        'id': 1,
        'name': '청해루',
        'addr': '자동차시장1길 24-1',
        'review_list': [
            {
                'review_id': 1,
                'score': 3,
                'comment': '좋지못했다'
            },
            {
                'review_id': 2,
                'score': 4,
                'comment': '상당한 맛이었다'
            }

        ],
    },
    {
        'id': 2,
        'name': '싸다김밥',
        'addr': '성동구 천호대로 380-7',
        'review_list': [],
    },
    {
        'id': 3,
        'name': '푶푶초밥',
        'addr': '성동구 천호대로 333-434',
        'review_list': [],
    },        
]

@app.get('/stores')
def store_list(request:Request):
    return templates.TemplateResponse(
        request=request,
        name='store_list.html',
        context={ 'food_store_list': food_store_list }
    )

@app.get('/stores/{store_id}')
def store_detail(request:Request, store_id: int):
    food_store = find_food_store_by_id(store_id)
    review_count = len(food_store['review_list'])
    avg_score = 0 if review_count == 0 else round(sum([review['score'] for review in food_store['review_list']]) / review_count, 1)
    
    return templates.TemplateResponse(
        request=request,
        name='store_detail.html',
        context={ 
            'food_store': food_store,
            'avg_score': avg_score,
            'review_count': review_count,
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
    food_store = find_food_store_by_id(store_id)
    food_store['review_list'].append({
        'review_id': get_new_review_id(food_store['review_list']),
        'score': score,
        'comment': comment,
    })
    return RedirectResponse(f'/stores/{store_id}', status_code=303)

@app.get('/stores/{store_id}/review/{review_id}/edit')
def review_edit(request:Request, store_id: int, review_id: int):
    review = find_review_by_id(review_id, store_id)
    
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
    review = find_review_by_id(review_id, store_id)
    review['score'] = score
    review['comment'] = comment
    return RedirectResponse(f'/stores/{store_id}', status_code=303)

@app.get('/stores/{store_id}/review/{review_id}/delete')
def review_delete(store_id: int, review_id: int):
    food_store = find_food_store_by_id(store_id)
    find_review = find_review_by_id(review_id, store_id)
    food_store['review_list'] = [review for review in food_store['review_list'] if review['review_id'] != find_review['review_id']]
    return RedirectResponse(f'/stores/{store_id}', status_code=303)

def find_food_store_by_id(store_id: int):
    return next((food_store for food_store in food_store_list if food_store['id'] == store_id), None)

def find_review_by_id(review_id: int, store_id: int):
    food_store = find_food_store_by_id(store_id)
    return next((review for review in food_store['review_list'] if review['review_id'] == review_id), None)

def get_new_review_id(review_list):
    return max([review['review_id'] for review in review_list], default=0) + 1
