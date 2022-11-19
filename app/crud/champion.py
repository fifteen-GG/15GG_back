from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.champion import Champion
from app.schemas.champion import ChampionCreate, ChampionUpdate


class CRUDChampion(CRUDBase[Champion, ChampionCreate, ChampionUpdate]):
    # Declare model specific CRUD operation methods.
    def create_champion(self, db: Session, summoner_info):
        summoner_id = summoner_info['id']
        try:
            champions = summoner_info['champions']
        except:
            return
        # todo
        for index, champion in enumerate(champions):
            try:
                champion_info = Champion(champion_name=champion['champion_name'], counts=champion['counts'], kills=champion['kills'],
                                         deaths=champion['deaths'], assists=champion['assists'], wins=champion['wins'], order=index + 1, summoner_id=summoner_id)
                db.add(champion_info)
                db.commit()
                if index >= 2:
                    return
            except:
                return
        return

    def update_champiion(self, db: Session):
        return


champion = CRUDChampion(Champion)
