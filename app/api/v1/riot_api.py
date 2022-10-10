from ast import And
from audioop import reverse
import datetime
import math
from urllib.error import HTTPError
import json
import httpx
from typing import Union
from fastapi import HTTPException, APIRouter
from dotenv import dotenv_values
import operator

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
            'win_rate': math.floor(league_info['wins'] / (league_info['wins'] + league_info['losses']) * 100),
            'win': league_info['wins'],
            'losses': league_info['losses']
        }
    return summoner_league_info


async def get_match_average_data(puuid: str):
    async with httpx.AsyncClient() as client:
        kills = 0
        deaths = 0
        assists = 0
        team_position = {}
        url = RIOT_API_ROOT_ASIA + '/match/v5/matches/by-puuid/' + \
            puuid+'/ids?type=ranked&start=0&count=20'
        match_list = await client.get(url, headers=HEADER)
        match_list = match_list.json()
        match_list_len = len(match_list)
        champions = []

        # 랭겜 이력이 없으면 ValueError
        if (match_list_len == 0):
            raise ValueError

        for match_id in match_list:
            url = RIOT_API_ROOT_ASIA + '/match/v5/matches/' + match_id
            match_info = await client.get(url, headers=HEADER)
            match_info = match_info.json()
            participants = match_info['metadata']['participants']
            user_index = participants.index(puuid)
            user_data = match_info['info']['participants'][user_index]
            kills += user_data['kills']
            deaths += user_data['deaths']
            assists += user_data['assists']
            championName = user_data['championName']
            win = user_data['win']
            flag = False

            for champion in champions:
                if champion['championName'] == championName:
                    flag = True
                    champion['counts'] += 1
                    champion['kills'] += user_data['kills']
                    champion['deaths'] += user_data['deaths']
                    champion['assists'] += user_data['assists']
                    if win:
                        champion['wins'] += 1
            if flag == False:
                champion_dict = {'championName': championName, 'counts': 1,
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

        sorted_champions = sorted(
            champions, key=lambda champion: (champion['counts'], champion['wins']), reverse=True)

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


async def get_match_list(puuid: str, page: str):
    async with httpx.AsyncClient() as client:
        match_info_list = []
        url = RIOT_API_ROOT_ASIA + '/match/v5/matches/by-puuid/' + \
            puuid+'/ids?start=' + str((int(page) - 1) * 5) + '&count=5'
        match_list = await client.get(url, headers=HEADER)
        match_list = match_list.json()
        if (len(match_list) == 0):
            raise HTTPException(status_code=404, detail='no matches')
        for match_id in match_list:
            url = RIOT_API_ROOT_ASIA + '/match/v5/matches/' + match_id
            match_info = await client.get(url, headers=HEADER)
            match_info = match_info.json()

            time_stamp = match_info['info']['gameStartTimestamp']
            datetime_obj = datetime.date.fromtimestamp(time_stamp/1000)

            participants = match_info['metadata']['participants']
            user_index = participants.index(puuid)
            user_data = match_info['info']['participants'][user_index]

            win = user_data['win']
            created_at = datetime_obj
            game_duration = match_info['info']['gameDuration']
            queue_id = match_info['info']['queueId']
            queue_mode = ''
            with open('./app/assets/queue.json', mode='r', encoding='UTF-8') as queueFile:
                queue_data_list = json.loads(queueFile.read())
                for queue_data in queue_data_list:
                    if queue_data['queueId'] == queue_id:
                        queue_mode = queue_data['description']
                        break
            summoner1Id = user_data['summoner1Id']
            summoner2Id = user_data['summoner2Id']
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
            champion_name = user_data['championName']
            kills = user_data['kills']
            deaths = user_data['deaths']
            assists = user_data['assists']

            try:
                kda = round((kills+assists) / deaths, 2)
            except ZeroDivisionError:
                kda = 'Perfect'
            cs = user_data['totalMinionsKilled'] + \
                user_data['neutralMinionsKilled']
            cs_per_min = round(cs / (game_duration / 60), 1)
            vision_wards_bought_in_game = user_data['visionWardsBoughtInGame']
            items = [user_data['item0'], user_data['item1'], user_data['item2'],
                     user_data['item3'], user_data['item4'], user_data['item5'], user_data['item6']]
            perks = {"perk": user_data['perks']
                     ['styles'][0]['selections'][0]['perk'],
                     "perkStyle": user_data['perks']
                     ['styles'][1]['style']}
            match_info_list.append(
                {'match_id': match_id,
                 'win': win, 'created_at': created_at,
                 'queue_mode': queue_mode, 'champion_name': champion_name,
                 'kills': kills, 'deaths': deaths, 'assists': assists,
                 'kda': kda, 'cs': cs, 'cs_per_min': cs_per_min,
                 'vision_wards_bought_in_game': vision_wards_bought_in_game, 'items': items, 'spells': spells, 'perks': perks})
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


def set_dictionary(src, dest, src_keys, dest_keys):
    for src_key, dest_key in zip(src_keys, dest_keys):
        dest[dest_key] = src[src_key]


@router.get('/user/{summoner_name}')
async def get_summoner(summoner_name: str):
    summoner_info = {}
    summoner_basic_info = await get_summoner_basic_info(summoner_name)

    summoner_id = summoner_basic_info['id']  # SUMMONER에서 사용
    puuid = summoner_basic_info['puuid']  # MATCH에서 사용
    summoner_info['name'] = summoner_basic_info['name']
    summoner_info['level'] = summoner_basic_info['summonerLevel']
    summoner_info['profileIconId'] = summoner_basic_info['profileIconId']

    summoner_league_info = await get_summoner_league_info(summoner_id)

    try:
        summoner_info['flex'] = summoner_league_info['RANKED_FLEX_SR']
    except KeyError:
        summoner_info['flex'] = None

    try:
        summoner_info['solo'] = summoner_league_info['RANKED_SOLO_5x5']
    except KeyError:
        summoner_info['solo'] = None

    avg_key_list = ['kda_avg', 'kills_avg', 'deaths_avg',
                    'assists_avg', 'prefer_position', 'champions']
    key_list = ['kda', 'kills', 'deaths',
                'assists', 'prefer_position', 'champions']
    # 자랭 솔랭 둘 다 none이면 무조건 랭겜 안돌린거고 get_match_average_data에서 뽑아낼 거 없음
    if summoner_info['flex'] == None and summoner_info['solo'] == None:
        none_list = {'kda': None, 'kills': None,
                     'deaths': None, 'assists': None, 'prefer_position': None, 'champions': None}
        set_dictionary(none_list, summoner_info, key_list, avg_key_list)
        return summoner_info

    match_average_data = await get_match_average_data(puuid)
    set_dictionary(match_average_data, summoner_info, key_list, avg_key_list)

    return summoner_info


@router.get('/match/{summoner_name}')
async def get_match_info(summoner_name: str, page: str):
    summoner_basic_info = await get_summoner_basic_info(summoner_name)
    puuid = summoner_basic_info['puuid']
    match_info = await get_match_list(puuid, page)
    return match_info


@router.get('/match/preview/{match_id}')
async def get_match_preview(match_id: str):
    match_preview_info = await get_match_preview_info(match_id)
    return match_preview_info
