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
                'score': 3,
                'comment': '좋지못했다'
            },
            {
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
    food_store = next((food_store for food_store in food_store_list if food_store['id'] == store_id), None)
    review_count = len(food_store['review_list'])
    avg_score = sum([review['score'] for review in food_store['review_list']]) / review_count
    
    return templates.TemplateResponse(
        request=request,
        name='store_detail.html',
        context={ 
            'food_store': food_store,
            'avg_score': avg_score,
            'review_count': review_count,
        }
    )