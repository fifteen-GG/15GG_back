from functools import cache
from operator import and_
from sqlalchemy.orm import Session
from app.crud import summoner
from app.crud.base import CRUDBase
from app.models.rank import Rank
from app.schemas.rank import RankCreate, RankUpdate
from sqlalchemy import and_


class CRUDRank(CRUDBase[Rank, RankCreate, RankUpdate]):
    # Declare model specific CRUD operation methods.
    def create_update_rank(self, db: Session, summoner_info, mode: str):
        flex = None
        solo = None
        if summoner_info['flex'] != None:
            flex_info = summoner_info['flex']
            flex = Rank(summoner_id=summoner_info['id'], tier=flex_info['tier'], rank=flex_info['rank'],
                        lp=flex_info['lp'], wins=flex_info['wins'], losses=flex_info['losses'], is_flex=True)

            cached_data = db.query(self.model).filter(self.model.summoner_id ==
                                                      summoner_info['id'] and self.model.is_flex == True).all()
            if len(cached_data) == 0:
                db.add(flex)
                db.commit()
            else:
                if mode == 'u':
                    db.query(self.model).filter(self.model.summoner_id ==
                                                summoner_info['id'] and self.model.is_flex == True)
        if summoner_info['solo'] != None:
            solo_info = summoner_info['solo']
            solo = Rank(summoner_id=summoner_info['id'], tier=solo_info['tier'], rank=solo_info['rank'],
                        lp=solo_info['lp'], wins=solo_info['wins'], losses=solo_info['losses'], is_flex=False)

            cached_data = db.query(self.model).filter(and_(self.model.summoner_id ==
                                                      summoner_info['id'], self.model.is_flex == False)).all()
            if len(cached_data) == 0:
                db.add(solo)
                db.commit()
            else:
                if mode == 'u':
                    db.query(self.model).filter(self.model.summoner_id ==
                                                summoner_info['id'] and self.model.is_flex == False)
        return {'flex': flex, 'solo': solo}

    def update_rank(self, db: Session):
        return


rank = CRUDRank(Rank)
