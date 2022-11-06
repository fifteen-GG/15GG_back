import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core import settings

from fastapi_utils.tasks import repeat_every

from app.api.v1.train_game import train_game_post
app = FastAPI(title=settings.PROJECT_NAME)
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix=settings.API_ROOT)

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)


# @app.on_event("startup")
# @repeat_every(seconds=60 * 1)
# async def periodic():
#     await train_game_post()
