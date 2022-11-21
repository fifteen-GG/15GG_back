from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud
from app.api.deps import get_db

router = APIRouter()


@router.get('', response_model=schemas.Code)
def code_create(*, db: Session = Depends(get_db)):
    '''
    Generate code
    '''
    code = crud.code.create_code(db)
    return code


@router.get('/validate')
def code_validate(*, db: Session = Depends(get_db), value: str):
    '''
    Validate code
    '''
    code = crud.code.validate_code(db, value)
    if len(code) < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No code with given value is found')

    crud.code.remove(db, model_id=code[0].value)

    if datetime.now() - code[0].created_at > timedelta(minutes=5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Code has expired')

    return {'message': 'Code validated'}


@router.post('/update/match_id')
def update_match_id(*, db: Session = Depends(get_db), code: str, match_id: str):
    crud.code.update_code(db, code, match_id)
