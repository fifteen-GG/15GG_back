from typing import Optional, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.train_game import TrainGame
from app.schemas.train_game import TrainGameCreate, TrainGameUpdate


class CRUDTrainGame(CRUDBase[TrainGame, TrainGameCreate, TrainGameUpdate]):
    # Declare model specific CRUD operation methods.
    pass


train_game = CRUDTrainGame(TrainGame)
