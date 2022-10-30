from typing import Optional, List

from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.train_game import TrainGame
from app.schemas.train_game import TrainGameCreate, TrainGameUpdate


class CRUDTrainGame(CRUDBase[TrainGame, TrainGameCreate, TrainGameUpdate]):
    # Declare model specific CRUD operation methods.
    def create_train_game(self, db: Session, match_id_set):
        match_id_list = list(match_id_set)
        query = ""
        for match_id in match_id_list:
            if query == "":
                query = f"('{match_id}', false)"
            else:
                query += f",('{match_id}', false)"

        db.execute(
            f"INSERT INTO train_game (match_id, is_parsed) VALUES {query} ON CONFLICT (match_id) DO NOTHING")
        db.commit()
        return

    def get_train_game(self, db: Session):
        # res = db.execute(
        #     'SELECT * from train_game WHERE is_parsed=false')
        # db.commit()
        train_game_list = db.query(self.model).filter(
            self.model.is_parsed == False).all()
        return train_game_list


train_game = CRUDTrainGame(TrainGame)
