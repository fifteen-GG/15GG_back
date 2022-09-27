from fastapi import APIRouter

from app.api.v1 import game, code, riot_api

api_router = APIRouter()
api_router.include_router(game.router, prefix="/game", tags=["games"])
api_router.include_router(code.router, prefix="/code", tags=["codes"])
api_router.include_router(riot_api.router, prefix="/riot", tags=["riot"])
