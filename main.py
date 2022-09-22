from email import header
from typing import Union
from fastapi import FastAPI, Header
import httpx

app = FastAPI()

HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": "RGAPI-d7162a7f-7e78-4266-9918-5e9a24ac2fd2"
}


async def get_summoner_basic_info(summoner_name: str):
    url = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+summoner_name
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADER)
        response = response.json()
    return response


async def get_summoner_league_info(summoner_id: str):
    url = 'https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/'+summoner_id
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADER)
        response = response.json()
    summoner_league_info = {}
    for i in response:
        if (i['queueType'] == 'RANKED_FLEX_SR'):
            summoner_league_info['flex'] = {
                'tier': i['tier'],
                'rank': i['rank'],
                'lp': i['leaguePoints'],
                'win_rate': i['wins'] / (i['wins'] + i['losses']) * 100,
                'win': i['wins'],
                'losses': i['losses']
            }
        else:
            summoner_league_info['solo'] = {
                'tier': i['tier'],
                'rank': i['rank'],
                'lp': i['leaguePoints'],
                'win_rate': i['wins'] / (i['wins'] + i['losses']) * 100,
                'win': i['wins'],
                'losses': i['losses']
            }
    return summoner_league_info


async def get_match_average_data(puuid: str):
    async with httpx.AsyncClient() as client:
        kda = 0
        kill = 0
        death = 0
        assist = 0
        position = {}
        i = 0
        while True:
            url = 'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/' + \
                puuid+'/ids?start=' + str(i) + '&count=1'
            match_id = await client.get(url, headers=HEADER)
            match_id = match_id.json()
            if len(match_id) == 0:
                break
            print(match_id)
            i = i + 1


@ app.get("/user/{summoner_name}")
async def get_summoner(summoner_name: str):
    summoner_info = {}
    summoner_basic_info = await get_summoner_basic_info(summoner_name)
    summoner_id = summoner_basic_info['id']  # SUMMONER에서 사용
    puuid = summoner_basic_info['puuid']  # MATCH에서 사용
    summoner_info['name'] = summoner_basic_info['name']
    summoner_info['profileIconId'] = summoner_basic_info['profileIconId']

    summoner_league_info = await get_summoner_league_info(summoner_id)
    summoner_info['flex'] = summoner_league_info['flex']
    summoner_info['solo'] = summoner_league_info['solo']

    match_average_data = await get_match_average_data(puuid)
    return {"summoner_id": summoner_id, "puuid": puuid}


async def get_game_list():
    async with httpx.AsyncClient() as client:
        games = []
        puuid = await get_summoner('정잭영')
        url = 'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/' + \
            puuid+'/ids?start=0&count=5'
        game_list = await client.get(url, headers=HEADER)
        game_list = game_list.json()
        # for game_id in game_list:
        game_info = await get_game_info(game_list[0])
        games.append(game_info)
        return games[0]['info']['participants'][0]


async def get_game_info(game_id: str):
    async with httpx.AsyncClient() as client:
        url = 'https://asia.api.riotgames.com/lol/match/v5/matches/'+game_id
        game_info = await client.get(url, headers=HEADER)
        game_info = game_info.json()
        return game_info
