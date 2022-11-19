from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.champion import Champion
from app.models.summoner import Summoner
from app.schemas.summoner import SummonerCreate, SummonerUpdate
from app.models.rank import Rank
from sqlalchemy import func


class CRUDSummoner(CRUDBase[Summoner, SummonerCreate, SummonerUpdate]):
    # Declare model specific CRUD operation methods.
    def get_summoner(self, db: Session, summoner_name: str):
        summoner_info = db.query(self.model).filter(
            func.lower(self.model.name) == summoner_name.lower()).one()
        rank_list = db.query(Rank).filter(
            summoner_info.id == Rank.summoner_id).all()
        flex = None
        solo = None
        return_champion_list = []
        for rank in rank_list:
            if rank.is_flex == True:
                flex = {'tier': rank.tier, 'rank': rank.rank, 'lp': rank.lp, 'wins': rank.wins, 'losses': rank.losses
                        }
            else:
                solo = {'tier': rank.tier, 'rank': rank.rank, 'lp': rank.lp, 'wins': rank.wins, 'losses': rank.losses
                        }
        champion_list = db.query(Champion).filter(
            summoner_info.id == Champion.summoner_id).order_by(Champion.order).all()
        for champion in champion_list:
            return_champion_list.append({'champion_name': champion.champion_name,
                                        'counts': champion.counts, 'kills': champion.kills, 'deaths': champion.deaths, 'assists': champion.assists, 'wins': champion.wins})
        return_summoner_info = {
            'id': summoner_info.id,
            'puuid': summoner_info.puuid,
            'name': summoner_info.name,
            'level': summoner_info.level,
            'profile_icon_id': summoner_info.profile_icon_id,
            'flex': flex,
            'solo': solo,
            'kda_avg': summoner_info.kda_avg,
            'kills_avg': summoner_info.kills_avg,
            'deaths_avg': summoner_info.deaths_avg,
            'assists_avg': summoner_info.assists_avg,
            'prefer_position': {summoner_info.prefer_position: summoner_info.prefer_position_rate},
            'champions': return_champion_list
        }

        return return_summoner_info

    def create_summoner(self, db: Session, summoner_info):
        if summoner_info['prefer_position'] == None:
            summoner_info['prefer_position'] = {None: None}
        prefer_position = list(summoner_info['prefer_position'].keys())[0]
        prefer_position_rate = list(
            summoner_info['prefer_position'].values())[0]

        summoner = Summoner(id=summoner_info['id'], puuid=summoner_info['puuid'], name=summoner_info['name'],
                            level=summoner_info['level'], profile_icon_id=summoner_info['profile_icon_id'], kda_avg=summoner_info['kda_avg'], kills_avg=summoner_info['kills_avg'], deaths_avg=summoner_info['deaths_avg'], assists_avg=summoner_info['assists_avg'], prefer_position=prefer_position, prefer_position_rate=prefer_position_rate)
        try:
            db.add(summoner)
            db.commit()
        except:
            return
        return

    def update_summoner(self, db: Session):
        return


summoner = CRUDSummoner(Summoner)
