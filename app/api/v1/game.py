from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud
from app.api.deps import get_db

router = APIRouter()


@router.get('', response_model=List[schemas.Game])
def game_list(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    '''
    Get list of games
    '''
    games = crud.game.get_multi(db, skip=skip, limit=limit)
    return games
