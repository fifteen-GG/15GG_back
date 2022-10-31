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
        train_game_list = db.query(self.model).filter(
            self.model.is_parsed == False).all()
        return train_game_list

    def update_is_parsed(self, db: Session, file_name):
        match_id = file_name.split('.')[0]

        db.query(self.model).filter(self.model.match_id ==
                                    match_id).update({self.model.is_parsed: True})
        db.commit()


train_game = CRUDTrainGame(TrainGame)
