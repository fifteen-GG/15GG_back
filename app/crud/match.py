from app.crud.base import CRUDBase
from app.models.match import Match
from app.schemas.match import MatchCreate, MatchUpdate
from sqlalchemy.orm import Session


class CrudMatch(CRUDBase[Match, MatchCreate, MatchUpdate]):
    # Declare model specific CRUD operation methods.
    def get_match_info(self, db: Session, match_id: str):
        try:
            match_info = db.query(self.model).filter(
                self.model.id == match_id).one()
            return match_info
        except:
            raise Exception

    def create_match(self, db: Session, match_info):
        match_data = Match(
            id=match_info['match_id'],
            queue_mode=match_info['queue_mode'],
            game_duration=match_info['game_duration'],
            created_at=match_info['created_at'])
        try:
            db.add(match_data)
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception
        return


match = CrudMatch(Match)
