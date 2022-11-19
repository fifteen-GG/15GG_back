from sqlalchemy.orm import Session
from app.crud import summoner
from app.crud.base import CRUDBase
from app.models.rank import Rank
from app.schemas.rank import RankCreate, RankUpdate


class CRUDRank(CRUDBase[Rank, RankCreate, RankUpdate]):
    # Declare model specific CRUD operation methods.
    def create_rank(self, db: Session, summoner_info):
        if summoner_info['flex'] == None:
            flex = None
        else:
            flex_info = summoner_info['flex']
            flex = Rank(summoner_id=summoner_info['id'], tier=flex_info['tier'], rank=flex_info['rank'],
                        lp=flex_info['lp'], wins=flex_info['wins'], losses=flex_info['losses'], is_flex=True)
            db.add(flex)
            db.commit()
        if summoner_info['solo'] == None:
            solo = None
        else:
            solo_info = summoner_info['solo']
            solo = Rank(summoner_id=summoner_info['id'], tier=solo_info['tier'], rank=solo_info['rank'],
                        lp=solo_info['lp'], wins=solo_info['wins'], losses=solo_info['losses'], is_flex=False)
            db.add(solo)
            db.commit()
        return {'flex': flex, 'solo': solo}

    def update_rank(self, db: Session):
        return


rank = CRUDRank(Rank)
