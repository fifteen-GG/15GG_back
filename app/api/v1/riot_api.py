import asyncio
import datetime
import math
import json
from tokenize import Number
import httpx
from fastapi import HTTPException, APIRouter
from dotenv import dotenv_values
import time
from bs4 import BeautifulSoup


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


async def get_match_data(match_id: str, client):
    url = RIOT_API_ROOT_ASIA + '/match/v5/matches/' + match_id
    try:
        match_info = await client.get(url, headers=HEADER)
        match_info.raise_for_status()
    except Exception as e:
        print(e)
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
        raise ValueError

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
                break
        if flag == False:
            champion_dict = {'championName': championName, 'counts': 1,
                             'kills': user_data['kills'], 'deaths': user_data['deaths'], 'assists': user_data['assists']}
            if win:
                champion_dict['wins'] = 1
            else:
                champion_dict['wins'] = 0
            champions.append(champion_dict)
    sorted_champions = sorted(champions, key=lambda champion: (
        champion['counts'], champion['wins']), reverse=True)

    if user_data['teamPosition'] in team_position:
        team_position[user_data['teamPosition']] += 1
    else:
        team_position[user_data['teamPosition']] = 1

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
            try:
                match_info['info']['gameEndTimestamp']
            except KeyError:
                game_duration = game_duration / 1000
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
                 'game_duration': game_duration,
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


def set_dictionary(dest, src, dest_keys, src_keys):
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

    request_list = [get_summoner_league_info(
        summoner_id), get_match_average_data(puuid)]
    response = await asyncio.gather(*request_list)
    summoner_league_info = response[0]
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
        set_dictionary(summoner_info, none_list, avg_key_list, key_list)
        return summoner_info

    match_average_data = response[1]
    set_dictionary(summoner_info, match_average_data, avg_key_list, key_list)
    return summoner_info


@router.get('/user/match_list/{summoner_name}')
async def get_match_info(summoner_name: str, page: str):
    summoner_basic_info = await get_summoner_basic_info(summoner_name)
    puuid = summoner_basic_info['puuid']
    match_info = await get_match_list(puuid, page)

    return match_info


@router.get('/match/preview/{match_id}')
async def get_match_preview(match_id: str):
    match_preview_info = await get_match_preview_info(match_id)
    return match_preview_info


@router.get('/match/detail/{match_id}')
async def get_match_detail(match_id: str):
    return_value = []
    red_team = {}
    blue_team = {}
    red_participants = []
    blue_participants = []
    red_avg = {'golds': 0, 'level': 0, 'kills': 0}
    blue_avg = {'golds': 0, 'level': 0, 'kills': 0}
    async with httpx.AsyncClient() as client:
        url = 'http://fow.kr/api_new_ajax.php'
        match_id_num = int(match_id.split('_')[1])
        try:
            response = await client.post(url, data={'action': 'battle_detail', 'gid': match_id_num})
        except:
            raise HTTPException(status_code=404, detail='Match is not found')
        user_rows = BeautifulSoup(
            response.text, features='html.parser').findAll('tr')

        for user_row in user_rows:
            try:
                summoner_name = user_row.find(
                    'td', class_='detail_list_name').text
                rank = user_row.find('td').text
            except:
                continue
            if user_row.find('td')['class'][0] == 't_purple':
                red_participants.append(
                    {'summonerName': summoner_name, 'rank': rank})
            else:
                blue_participants.append(
                    {'summonerName': summoner_name, 'rank': rank})
    async with httpx.AsyncClient() as client:
        match_info = await get_match_data(match_id, client)
        participants = match_info['info']['participants']
        for participant in participants:
            summoner_name = participant['summonerName']
            team_id = participant['teamId']
            champion_name = participant['championName']
            champ_level = participant['champLevel']
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
            perks = {"perk": participant['perks']['styles'][0]['selections'][0]['perk'],
                     "perkStyle": participant['perks']['styles'][1]['style']}
            items = [participant['item0'], participant['item1'], participant['item2'],
                     participant['item3'], participant['item4'], participant['item5'], participant['item6']]
            gold_earned = participant['goldEarned']
            kills = participant['kills']
            deaths = participant['deaths']
            assists = participant['assists']
            total_damage_dealt_to_champions = participant['totalDamageDealtToChampions']
            total_damage_taken = participant['totalDamageTaken']
            win = participant['win']
            if team_id == 100:
                blue_avg['golds'] += gold_earned
                blue_avg['kills'] += kills
                blue_avg['level'] += champ_level
                for index, blue_participant in enumerate(blue_participants):
                    if blue_participant['summonerName'] == summoner_name:
                        blue_participants[index] = {'summonerName': summoner_name, 'championName': champion_name, 'rank': blue_participant['rank'], 'champLevel': champ_level, 'spells': spells, 'perks': perks, 'items': items, 'goldEarned': gold_earned, 'kills': kills,
                                                    'deaths': deaths, 'assists': assists, 'totalDamageDealtToChampions': total_damage_dealt_to_champions, 'totalDamageTake': total_damage_taken, 'win': win}
                        break
            else:
                red_avg['golds'] += gold_earned
                red_avg['kills'] += kills
                red_avg['level'] += champ_level
                for index, red_participant in enumerate(red_participants):
                    if red_participant['summonerName'] == summoner_name:
                        red_participants[index] = {'summonerName': summoner_name, 'championName': champion_name, 'rank': blue_participant['rank'], 'champLevel': champ_level, 'spells': spells, 'perks': perks, 'items': items, 'goldEarned': gold_earned, 'kills': kills,
                                                   'deaths': deaths, 'assists': assists, 'totalDamageDealtToChampions': total_damage_dealt_to_champions, 'totalDamageTake': total_damage_taken, 'win': win}
                        break
    return [{'team': 'red', 'teamAvgData': {'golds': red_avg['golds']/5, 'kills':red_avg['kills']/5, 'level':red_avg['level']/5}, 'participants': red_participants}, {'team': 'blue', 'teamAvgData': {'golds': blue_avg['golds']/5, 'kills':blue_avg['kills']/5, 'level':blue_avg['level']/5}, 'participants': blue_participants}]
