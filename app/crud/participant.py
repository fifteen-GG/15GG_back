from typing import Optional, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.participant import Participant
from app.schemas.participant import ParticipantCreate, ParticipantUpdate
from sqlalchemy import func


class CrudParticipant(CRUDBase[Participant, ParticipantCreate, ParticipantUpdate]):
    # Declare model specific CRUD operation methods.
    def get_participant_list(self, db: Session, page: str, summoner_name: str):
        try:
            participant_list = db.query(self.model).filter(
                func.lower(self.model.summoner_name) == summoner_name.lower()).order_by(self.model.match_id.desc()).offset((int(page) - 1) * 5).limit(5).all()
            return participant_list
        except:
            return

    def get_participant_by_match_id(self, db: Session, match_id: str):
        try:
            participant_list = db.query(self.model).filter(
                self.model.match_id == match_id).all()
            if len(participant_list) == 0:
                raise Exception
            return participant_list
        except:
            print("jhello")
            raise Exception

    def create_participant(self, db: Session, participant_info):
        participant_data = Participant(match_id=participant_info['match_id'],
                                       summoner_name=participant_info['summoner_name'],
                                       champion_name=participant_info['champion_name'],
                                       team_id=participant_info['team_id'],
                                       rank=participant_info['rank'], tier=participant_info['tier'],
                                       champion_level=participant_info['champion_level'],
                                       spell1=participant_info['spells']['spell1'],
                                       spell2=participant_info['spells']['spell2'],
                                       perk=participant_info['perks']['perk'],
                                       perk_style=participant_info['perks']['perk_style'],
                                       item0=participant_info['items'][0],
                                       item1=participant_info['items'][1],
                                       item2=participant_info['items'][2],
                                       item3=participant_info['items'][3],
                                       item4=participant_info['items'][4],
                                       item5=participant_info['items'][5],
                                       item6=participant_info['items'][6],
                                       gold_earned=participant_info['gold_earned'],
                                       kills=participant_info['kills'],
                                       deaths=participant_info['deaths'],
                                       assists=participant_info['assists'],
                                       total_damage_dealt_to_champions=participant_info[
                                           'total_damage_dealt_to_champions'],
                                       total_damage_taken=participant_info['total_damage_taken'],
                                       win=participant_info['win'],
                                       cs=participant_info['cs'],
                                       vision_wards_bought_in_game=participant_info[
                                           'vision_wards_bought_in_game'])
        db.add(participant_data)
        db.commit()
        return participant_data


participant = CrudParticipant(Participant)
