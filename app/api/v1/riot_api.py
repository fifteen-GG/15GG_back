import asyncio
from curses import pair_content
import datetime
import math
import json
from app import crud
from app.crud import summoner
import httpx
from fastapi import HTTPException, APIRouter, Depends
from dotenv import dotenv_values
import time
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.database.session import SessionLocal


env = dotenv_values('.env')
router = APIRouter()

origins = ['*']

HEADER = {
    'X-Riot-Token': env['RIOT_TOKEN']
}

RIOT_API_ROOT_KR = 'https://kr.api.riotgames.com/lol'
RIOT_API_ROOT_ASIA = 'https://asia.api.riotgames.com/lol'


async def get_summoner_basic_info(summoner_name: str):
    url = RIOT_API_ROOT_KR + '/summoner/v4/summoners/by-name/' + summoner_name
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=HEADER)
            response.raise_for_status()
        except:
            raise HTTPException(status_code=404, detail='user not found')
        response = response.json()
    return response


async def get_summoner_league_info(summoner_id: str):
    url = RIOT_API_ROOT_KR + '/league/v4/entries/by-summoner/'+summoner_id
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=HEADER)
            response.raise_for_status()
        except:
            raise HTTPException(status_code=404, detail='user not found')
        response = response.json()
    summoner_league_info = {}
    for league_info in response:
        mode = league_info['queueType']
        summoner_league_info[mode] = {
            'tier': league_info['tier'],
            'rank': league_info['rank'],
            'lp': league_info['leaguePoints'],
            'wins': league_info['wins'],
            'losses': league_info['losses']
        }
    return summoner_league_info


async def get_match_data(match_id: str, client):
    url = RIOT_API_ROOT_ASIA + '/match/v5/matches/' + match_id
    try:
        match_info = await client.get(url, headers=HEADER)
        match_info.raise_for_status()
    except Exception as e:
        print(e)
        return
    match_info = match_info.json()
    return match_info


async def get_match_average_data(puuid: str):
    client = httpx.AsyncClient()
    kills = 0
    deaths = 0
    assists = 0
    team_position = {}
    url = RIOT_API_ROOT_ASIA + '/match/v5/matches/by-puuid/' + \
        puuid+'/ids?type=ranked&start=0&count=10'
    match_list = await client.get(url, headers=HEADER)
    match_list = match_list.json()
    match_list_len = len(match_list)
    champions = []

    # 랭겜 이력이 없으면 ValueError
    if (match_list_len == 0):
        return None

    request_list = [get_match_data(match_id, client)
                    for match_id in match_list]
    match_info_list = await asyncio.gather(*request_list)
    for match_info in match_info_list:
        participants = match_info['metadata']['participants']
        user_index = participants.index(puuid)
        user_data = match_info['info']['participants'][user_index]
        kills += user_data['kills']
        deaths += user_data['deaths']
        assists += user_data['assists']
        champion_name = user_data['championName']
        win = user_data['win']
        flag = False

        for champion in champions:
            if champion['champion_name'] == champion_name:
                flag = True
                champion['counts'] += 1
                champion['kills'] += user_data['kills']
                champion['deaths'] += user_data['deaths']
                champion['assists'] += user_data['assists']
                if win:
                    champion['wins'] += 1
                break
        if flag == False:
            champion_dict = {'champion_name': champion_name, 'counts': 1,
                             'kills': user_data['kills'], 'deaths': user_data['deaths'], 'assists': user_data['assists']}
            if win:
                champion_dict['wins'] = 1
            else:
                champion_dict['wins'] = 0
            champions.append(champion_dict)
        if user_data['teamPosition'] in team_position:
            team_position[user_data['teamPosition']] += 1
        else:
            team_position[user_data['teamPosition']] = 1
    sorted_champions = sorted(champions, key=lambda champion: (
        champion['counts'], champion['wins']), reverse=True)
    prefer_position = max(team_position, key=team_position.get)
    position_rate = math.floor(
        team_position[prefer_position] / match_list_len * 100)
    if prefer_position == 'MIDDLE':
        prefer_position = 'MID'
    elif prefer_position == 'JUNGLE':
        prefer_position = 'JG'
    elif prefer_position == 'UTILITY':
        prefer_position = 'SUP'
    elif prefer_position == 'BOTTOM':
        prefer_position = 'ADC'

    try:
        kda = round((kills+assists) / deaths, 2)
    except ZeroDivisionError:
        kda = 'Perfect'

    match_average_data = {'kda': kda,
                          'kills': round(kills / match_list_len, 1),
                          'deaths': round(deaths / match_list_len, 1),
                          'assists': round(assists / match_list_len, 1),
                          'prefer_position': {prefer_position: position_rate},
                          'champions': sorted_champions
                          }
    return match_average_data


async def get_match_list(puuid: str, page: str, db: Session):
    async with httpx.AsyncClient() as client:
        match_info_list = []
        url = RIOT_API_ROOT_ASIA + '/match/v5/matches/by-puuid/' + \
            puuid+'/ids?start=' + str((int(page) - 1) * 5) + '&count=5'
        match_list = await client.get(url, headers=HEADER)
        match_list = match_list.json()
        if (len(match_list) == 0):
            raise HTTPException(status_code=404, detail='no matches')
        request_list = [get_match_data(match_id, client)
                        for match_id in match_list]
        response = await asyncio.gather(*request_list)

        for match_info in response:
            flag = False
            match_id = match_info['metadata']['matchId']
            time_stamp = match_info['info']['gameStartTimestamp']
            created_at = datetime.date.fromtimestamp(time_stamp/1000)
            queue_id = match_info['info']['queueId']
            queue_mode = ''
            with open('./app/assets/queue.json', mode='r', encoding='UTF-8') as queueFile:
                queue_data_list = json.loads(queueFile.read())
                for queue_data in queue_data_list:
                    if queue_data['queueId'] == queue_id:
                        queue_mode = queue_data['description']
                        break
            game_duration = match_info['info']['gameDuration']
            participants_data = match_info['info']['participants']
            try:
                crud.match.create_match(db, {"match_id": match_id, "queue_mode": queue_mode,
                                             "game_duration": game_duration, "created_at": created_at})
            except:
                flag = True
                pass
            for participant in participants_data:
                summoner_id = participant['summonerId']
                # tier_dict = await get_summoner_league_info(summoner_id)
                participant_puuid = participant['puuid']
                team_id = participant['teamId']
                summoner_name = participant['summonerName']
                champion_level = participant['champLevel']
                gold_earned = participant['goldEarned']
                win = participant['win']
                try:
                    match_info['info']['gameEndTimestamp']
                except KeyError:
                    game_duration = game_duration / 1000
                summoner1Id = participant['summoner1Id']
                summoner2Id = participant['summoner2Id']
                spells = {'spell1': '', 'spell2': ''}
                with open('./app/assets/spell.json', mode='r', encoding='UTF-8') as spellFile:
                    spell_data_list = json.loads(spellFile.read())['data']
                    for key, value in spell_data_list.items():
                        if value['key'] == str(summoner1Id):
                            spells['spell1'] = value['id']
                        elif value['key'] == str(summoner2Id):
                            spells['spell2'] = value['id']
                        if spells['spell1'] != '' and spells['spell2'] != '':
                            break
                champion_name = participant['championName']
                kills = participant['kills']
                deaths = participant['deaths']
                assists = participant['assists']
                total_damage_dealt_to_champions = participant['totalDamageDealtToChampions']
                total_damage_taken = participant['totalDamageTaken']
                try:
                    kda = round((kills+assists) / deaths, 2)
                except ZeroDivisionError:
                    kda = 'Perfect'
                cs = participant['totalMinionsKilled'] + \
                    participant['neutralMinionsKilled']
                cs_per_min = round(cs / (game_duration / 60), 1)
                vision_wards_bought_in_game = participant['visionWardsBoughtInGame']
                items = [participant['item0'], participant['item1'], participant['item2'],
                         participant['item3'], participant['item4'], participant['item5'], participant['item6']]
                perks = {"perk": participant['perks']['styles'][0]['selections'][0]['perk'],
                         "perk_style": participant['perks']['styles'][1]['style']}
                result = {'match_id': match_id, "summoner_name": summoner_name,
                          "tier": "Gold",
                          "rank": "Gold",
                          "team_id": team_id,
                          'champion_name': champion_name,
                          "champion_level": champion_level,
                          'gold_earned': gold_earned,
                          'game_duration': game_duration,
                          'win': win, 'created_at': created_at,
                          'queue_mode': queue_mode,
                          'kills': kills, 'deaths': deaths, 'assists': assists,
                          'total_damage_taken': total_damage_taken,
                          'total_damage_dealt_to_champions': total_damage_dealt_to_champions,
                          'kda': kda, 'cs': cs, 'cs_per_min': cs_per_min,
                          'vision_wards_bought_in_game': vision_wards_bought_in_game,
                          'items': items, 'spells': spells, 'perks': perks}
                if participant_puuid == puuid:
                    match_info_list.append(result)
                if flag == False:
                    try:
                        crud.participant.create_participant(db, result)
                    except:
                        pass
        return match_info_list


async def get_match_preview_info(match_id: str):
    red = []
    blue = []
    async with httpx.AsyncClient() as client:
        url = RIOT_API_ROOT_ASIA + '/match/v5/matches/' + match_id
        try:
            match_info = await client.get(url, headers=HEADER)
            match_info.raise_for_status()
        except:
            raise HTTPException(status_code=404, detail='match not found')
        match_info = match_info.json()
        participants_info = match_info['info']['participants']
        game_version = match_info['info']['gameVersion']
        game_creation = match_info['info']['gameCreation']
        datetimeobj = datetime.datetime.fromtimestamp(game_creation/1000)
    for participant_info in participants_info:
        profile = {"summonerName": participant_info['summonerName'],
                   "championName": participant_info['championName'],
                   "individualPosition": participant_info['individualPosition'],
                   "teamPosition": participant_info['teamPosition']
                   }
        if participant_info['teamId'] == 100:
            blue.append(profile)
        elif participant_info['teamId'] == 200:
            red.append(profile)

    return {"gameVersion": game_version, "red": red, "blue": blue, "gameCreation": datetimeobj}


def set_dictionary(dest, src, dest_keys, src_keys):
    for src_key, dest_key in zip(src_keys, dest_keys):
        dest[dest_key] = src[src_key]


@router.get('/user/{summoner_name}')
async def get_summoner(summoner_name: str, db: Session = Depends(get_db)):
    start = time.time()
    return_summoner_info = {
        'id': None,
        'puuid': None,
        'name': None,
        'level': None,
        'profile_icon_id': None,
        'flex': None,
        'solo': None,
        'kda_avg': None,
        'kills_avg': None,
        'deaths_avg': None,
        'assists_avg': None,
        'prefer_position': None,
        'champions': None
    }
    try:
        response = crud.summoner.get_summoner(db, summoner_name)
        print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
        return response
    except:
        summoner_basic_info = await get_summoner_basic_info(summoner_name)

        return_summoner_info['id'] = summoner_basic_info['id']
        return_summoner_info['puuid'] = summoner_basic_info['puuid']
        return_summoner_info['name'] = summoner_basic_info['name']
        return_summoner_info['level'] = summoner_basic_info['summonerLevel']
        return_summoner_info['profile_icon_id'] = summoner_basic_info['profileIconId']

        request_list = [get_summoner_league_info(
            return_summoner_info['id']), get_match_average_data(return_summoner_info['puuid'])]
        response = await asyncio.gather(*request_list)
        summoner_league_info = response[0]
        try:
            return_summoner_info['flex'] = summoner_league_info['RANKED_FLEX_SR']
        except KeyError:
            return_summoner_info['flex'] = None

        try:
            return_summoner_info['solo'] = summoner_league_info['RANKED_SOLO_5x5']
        except KeyError:
            return_summoner_info['solo'] = None

        avg_key_list = ['kda_avg', 'kills_avg', 'deaths_avg',
                        'assists_avg', 'prefer_position', 'champions']
        key_list = ['kda', 'kills', 'deaths',
                    'assists', 'prefer_position', 'champions']
    # 자랭 솔랭 둘 다 none이면 무조건 랭겜 안돌린거고 get_match_average_data에서 뽑아낼 거 없음
        if return_summoner_info['flex'] == None and return_summoner_info['solo'] == None:
            none_list = {'kda': None, 'kills': None, 'deaths': None,
                         'assists': None, 'prefer_position': None, 'champions': None}
            set_dictionary(return_summoner_info, none_list,
                           avg_key_list, key_list)
            crud.summoner.create_summoner(db, return_summoner_info)
            print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
            return return_summoner_info

        match_average_data = response[1]
        set_dictionary(return_summoner_info, match_average_data,
                       avg_key_list, key_list)
        crud.summoner.create_summoner(db, return_summoner_info)
        crud.rank.create_rank(db, return_summoner_info)
        crud.champion.create_champion(db, return_summoner_info)
        print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
        return return_summoner_info


@router.get('/user/match_list/{summoner_name}')
async def get_match_info(summoner_name: str, page: str, db: Session = Depends(get_db)):
    # summoner_name을 받으면 participant->summoner 테이블에 summoner_name이 있는지 try
    # 있으면? -> 이미 검색해본 이력이 있다. 해당 summoner가 포함된 게임이 db에 캐싱돼있음 1페이지 5개 보여주기
    # 없으면? -> 해당 summoner와 관련된 게임이 db에 캐싱돼있지 않음
    try:
        response = crud.summoner.get_summoner(db, summoner_name)
    except:  # 초기진입
        response = await get_summoner_basic_info(summoner_name)
        puuid = response['puuid']
        user_match_info = await get_match_list(puuid, page, db)
        return user_match_info
    try:
        user_match_info = []
        participant_list = crud.participant.get_participant_list(
            db, page, summoner_name)
        if len(participant_list) < 5:
            raise Exception('There is no cached game.')
        for participant in participant_list:
            print(participant.match_id)
            match_info = crud.match.get_match_info(db, participant.match_id)
            try:
                kda = round(
                    (participant.kills+participant.assists) / participant.deaths, 2)
            except ZeroDivisionError:
                kda = 'Perfect'
            user_match_info.append({'match_id': participant.match_id,
                                   'game_duration': match_info.game_duration, 'win': participant.win, 'created_at': match_info.created_at,
                                    'queue_mode': match_info.queue_mode, 'champion_name': participant.champion_name,
                                    'team_id': participant.team_id,
                                    'kills': participant.kills, 'deaths': participant.deaths, 'assists': participant.assists,
                                    'kda': kda, 'cs': participant.cs,
                                    'cs_per_min': round(participant.cs / (match_info.game_duration / 60), 1),
                                    'vision_wards_bought_in_game': participant.vision_wards_bought_in_game,
                                    'items': [participant.item0, participant.item1, participant.item2, participant.item3, participant.item4, participant.item5, participant.item6],
                                    'spells': {'spell1': participant.spell1, 'spell2': participant.spell2},
                                    'perks': {'perk': participant.perk, 'perk_style': participant.perk_style}
                                    })
    except:
        puuid = response['puuid']
        user_match_info = await get_match_list(puuid, page, db)

    return user_match_info


@ router.get('/match/preview/{match_id}')
async def get_match_preview(match_id: str):
    match_preview_info = await get_match_preview_info(match_id)
    return match_preview_info


@ router.get('/match/detail/{match_id}')
async def get_match_detail(match_id: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        try:
            participants = crud.participant.get_participant_by_match_id(
                db, match_id)
        except:
            match_info = await get_match_data(match_id, client)
            participants = match_info['info']['participants']
        red_participants = []
        blue_participants = []
        red_avg = {'golds': 0, 'level': 0, 'kills': 0}
        blue_avg = {'golds': 0, 'level': 0, 'kills': 0}
    # async with httpx.AsyncClient() as client:
    #     url = 'http://fow.kr/api_new_ajax.php'
    #     match_id_num = int(match_id.split('_')[1])
    #     try:
    #         response = await client.post(url, data={'action': 'battle_detail', 'gid': match_id_num})
    #     except:
    #         raise HTTPException(status_code=404, detail='Match is not found')
    #     user_rows = BeautifulSoup(
    #         response.text, features='html.parser').findAll('tr')

    #     for user_row in user_rows:
    #         try:
    #             summoner_name = user_row.find(
    #                 'td', class_='detail_list_name').text
    #             rank = user_row.find('td').text
    #         except:
    #             continue
    #         if user_row.find('td')['class'][0] == 't_purple':
    #             red_participants.append(
    #                 {'summonerName': summoner_name, 'rank': rank})
    #         else:
    #             blue_participants.append(
    #                 {'summonerName': summoner_name, 'rank': rank})
        for participant in participants:
            spells = {'spell1': '', 'spell2': ''}
            try:
                summoner_name = participant['summonerName']
                team_id = participant['teamId']
                champion_name = participant['championName']
                champ_level = participant['champLevel']
                summoner1Id = participant['summoner1Id']
                summoner2Id = participant['summoner2Id']
                with open('./app/assets/spell.json', mode='r', encoding='UTF-8') as spellFile:
                    spell_data_list = json.loads(spellFile.read())['data']
                    for key, value in spell_data_list.items():
                        if value['key'] == str(summoner1Id):
                            spells['spell1'] = value['id']
                        elif value['key'] == str(summoner2Id):
                            spells['spell2'] = value['id']
                        if spells['spell1'] != '' and spells['spell2'] != '':
                            break
                perks = {"perk": participant['perks']['styles'][0]['selections'][0]['perk'],
                         "perkStyle": participant['perks']['styles'][1]['style']}
                gold_earned = participant['goldEarned']
                total_damage_dealt_to_champions = participant['totalDamageDealtToChampions']
                total_damage_taken = participant['totalDamageTaken']
                items = [participant['item0'], participant['item1'], participant['item2'],
                         participant['item3'], participant['item4'], participant['item5'], participant['item6']]
                kills = participant['kills']
                deaths = participant['deaths']
                assists = participant['assists']
                win = participant['win']
            except:
                summoner_name = participant.summoner_name
                team_id = participant.team_id
                champion_name = participant.champion_name
                champ_level = participant.champion_level
                spells['spell1'] = participant.spell1
                spells['spell2'] = participant.spell2
                perks = {"perk": participant.perk,
                         "perkStyle": participant.perk_style}
                gold_earned = participant.gold_earned
                total_damage_dealt_to_champions = participant.total_damage_dealt_to_champions
                total_damage_taken = participant.total_damage_taken
                items = [participant.item0, participant.item1, participant.item2,
                         participant.item3, participant.item4, participant.item5, participant.item6]
                kills = participant.kills
                deaths = participant.deaths
                assists = participant.assists
                win = participant.win

            if team_id == 100:
                blue_avg['golds'] += gold_earned
                blue_avg['kills'] += kills
                blue_avg['level'] += champ_level
                blue_participants.append({'summoner_name': summoner_name, 'champion_name': champion_name, 'rank': 'gold', 'champ_level': champ_level, 'spells': spells, 'perks': perks, 'items': items, 'gold_earned': gold_earned, 'kills': kills,
                                          'deaths': deaths, 'assists': assists, 'total_damage_dealt_to_champions': total_damage_dealt_to_champions, 'total_damage_taken': total_damage_taken, 'win': win})
            else:
                red_avg['golds'] += gold_earned
                red_avg['kills'] += kills
                red_avg['level'] += champ_level
                red_participants.append({'summoner_name': summoner_name, 'champion_name': champion_name, 'rank': 'gold', 'champ_level': champ_level, 'spells': spells, 'perks': perks, 'items': items, 'gold_earned': gold_earned, 'kills': kills,
                                         'deaths': deaths, 'assists': assists, 'total_damage_dealt_to_champions': total_damage_dealt_to_champions, 'total_damage_taken': total_damage_taken, 'win': win})
        return [{'team': 'red', 'win': red_participants[0]['win'], 'team_avg_data': {'golds': red_avg['golds']/5, 'kills': red_avg['kills']/5, 'level': red_avg['level']/5}, 'participants': red_participants}, {'team': 'blue', 'win': blue_participants[0]['win'], 'team_avg_data': {'golds': blue_avg['golds']/5, 'kills': blue_avg['kills']/5, 'level': blue_avg['level']/5}, 'participants': blue_participants}]
