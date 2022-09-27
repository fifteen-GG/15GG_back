import datetime
from email import header
from math import floor
from typing import Union
from fastapi import FastAPI
import math
import httpx
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": "RGAPI-cb0b2e45-b6bc-4a81-b67f-2cec7269a28b"
}

KR_URL = "https://kr.api.riotgames.com/lol"
ASIA_URL = "https://asia.api.riotgames.com/lol"

json_path = './queue.json'


async def get_summoner_basic_info(summoner_name: str):
    url = KR_URL + '/summoner/v4/summoners/by-name/' + summoner_name
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADER)
        response = response.json()
    return response


async def get_summoner_league_info(summoner_id: str):
    url = KR_URL + '/league/v4/entries/by-summoner/'+summoner_id
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADER)
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
        kda = 0
        kills = 0
        deaths = 0
        assists = 0
        team_position = {}
        url = ASIA_URL + '/match/v5/matches/by-puuid/' + \
            puuid+'/ids?type=ranked&start=0&count=20'
        match_list = await client.get(url, headers=HEADER)
        match_list = match_list.json()
        for match_id in match_list:
            url = ASIA_URL + '/match/v5/matches/' + match_id
            match_info = client.get(url, headers=HEADER)
            print(match_info)
            # 429 에러 다루기
        #     match_info = match_info.json()
        #     participants = match_info['metadata']['participants']
        #     user_index = participants.index(puuid)
        #     user_data = match_info['info']['participants'][user_index]
        #     kda += user_data['challenges']['kda']
        #     kills += user_data['kills']
        #     deaths += user_data['deaths']
        #     assists += user_data['assists']

        #     if user_data['teamPosition'] in team_position:
        #         team_position[user_data['teamPosition']] += 1
        #     else:
        #         team_position[user_data['teamPosition']] = 1
        # prefer_position = max(team_position, key=team_position.get)
        # position_rate = math.floor(team_position[prefer_position] / 20 * 100)
        # if prefer_position == 'MIDDLE':
        #     prefer_position = 'MID'
        # elif prefer_position == 'JUNGLE':
        #     prefer_position = 'JG'
        # elif prefer_position == 'UTILITY':
        #     prefer_position = 'SUP'
        # elif prefer_position == 'BOTTOM':
        #     prefer_position = 'ADC'
        # match_average_data = {'kda': round(kda / 20, 2),
        #                       'kills': round(kills / 20, 1),
        #                       'deaths': round(deaths / 20, 1),
        #                       'assists': round(assists / 20, 1),
        #                       'prefer_position': {prefer_position: position_rate}
        #                       }
        return "match_average_data"


async def get_match_list(puuid: str, page: str):
    async with httpx.AsyncClient() as client:
        match_info_list = []
        url = ASIA_URL + '/match/v5/matches/by-puuid/' + \
            puuid+'/ids?start=' + str(int(page) * 5) + '&count=5'
        match_list = await client.get(url, headers=HEADER)
        match_list = match_list.json()
        for match_id in match_list:
            url = ASIA_URL + '/match/v5/matches/' + match_id
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
            queue_mode = ""
            with open(json_path, mode="r", encoding="UTF-8") as file:
                queue_data_list = json.loads(file.read())
                for queue_data in queue_data_list:
                    if queue_data['queueId'] == queue_id:
                        queue_mode = queue_data['description']
                        break
            champion_name = user_data['championName']
            kills = user_data['kills']
            deaths = user_data['deaths']
            assists = user_data['assists']
            kda = round(user_data['challenges']['kda'], 2)
            cs = user_data['totalMinionsKilled'] + \
                user_data['neutralMinionsKilled']
            cs_per_min = round(cs / (game_duration / 60), 1)
            vision_wards_bought_in_game = user_data['visionWardsBoughtInGame']
            items = [user_data['item0'], user_data['item1'], user_data['item2'],
                     user_data['item3'], user_data['item4'], user_data['item5'], user_data['item6']]
            match_info_list.append(
                {"match_id": match_id,
                 "win": win, "created_at": created_at,
                 "queue_mode": queue_mode, "champion_name": champion_name,
                 "kills": kills, "deaths": deaths, "assists": assists,
                 "kda": kda, "cs": cs, "cs_per_min": cs_per_min,
                 "vision_wards_bought_in_game": vision_wards_bought_in_game, "items": items})
        return match_info_list


@ app.get("/user/{summoner_name}")
async def get_summoner(summoner_name: str):
    summoner_info = {}
    summoner_basic_info = await get_summoner_basic_info(summoner_name)
    summoner_id = summoner_basic_info['id']  # SUMMONER에서 사용
    puuid = summoner_basic_info['puuid']  # MATCH에서 사용
    summoner_info['name'] = summoner_basic_info['name']
    summoner_info['level'] = summoner_basic_info['summonerLevel']
    summoner_info['profileIconId'] = summoner_basic_info['profileIconId']

    summoner_league_info = await get_summoner_league_info(summoner_id)
    summoner_info['flex'] = summoner_league_info['RANKED_FLEX_SR']
    summoner_info['solo'] = summoner_league_info['RANKED_SOLO_5x5']
    match_average_data = await get_match_average_data(puuid)
    summoner_info['kda_avg'] = match_average_data['kda']
    summoner_info['kills_avg'] = match_average_data['kills']
    summoner_info['deaths_avg'] = match_average_data['deaths']
    summoner_info['assists_avg'] = match_average_data['assists']
    summoner_info['prefer_position'] = match_average_data['prefer_position']
    return summoner_info


@app.get("/match/{summoner_name}")
async def get_match_info(summoner_name: str, page: str):
    summoner_basic_info = await get_summoner_basic_info(summoner_name)
    puuid = summoner_basic_info['puuid']
    match_info = await get_match_list(puuid, page)
    return match_info
