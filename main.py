from email import header
from math import floor
from typing import Union
from fastapi import FastAPI, Header
import math
import httpx

app = FastAPI()

HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": "RGAPI-50ecfaac-9f0c-4aec-8d36-bf4c0c6a4698"
}

URL = "https://kr.api.riotgames.com/lol"


async def get_summoner_basic_info(summoner_name: str):
    url = URL + '/summoner/v4/summoners/by-name/' + summoner_name
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADER)
        response = response.json()
    return response


async def get_summoner_league_info(summoner_id: str):
    url = URL + '/league/v4/entries/by-summoner/'+summoner_id
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
        counts = 0
        print(puuid)
        url = 'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/CUEFylEUWjMck_vyQBfASCn9LoNcxrJdoklHYjwdoZi6hPR7KOncpOI2gmefVfWGrATqaz_rpR0DgQ/ids?type=ranked&start=0&count=50'
        match_list = await client.get(url, headers=HEADER)
        match_list = match_list.json()
        for match_id in match_list:
            url = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + match_id
            match_info = await client.get(url, headers=HEADER)
            # 429 에러 다루기
            match_info = match_info.json()
            participants = match_info['metadata']['participants']
            user_index = participants.index(puuid)
            user_data = match_info['info']['participants'][user_index]
            kda += user_data['challenges']['kda']
            kills += user_data['kills']
            deaths += user_data['deaths']
            assists += user_data['assists']

            if user_data['teamPosition'] in team_position:
                team_position[user_data['teamPosition']] += 1
            else:
                team_position[user_data['teamPosition']] = 1
        prefer_position = max(team_position, key=team_position.get)
        position_rate = math.floor(team_position[prefer_position] / 50 * 100)
        if prefer_position == 'MIDDLE':
            prefer_position = 'MID'
        elif prefer_position == 'JUNGLE':
            prefer_position = 'JG'
        elif prefer_position == 'UTILITY':
            prefer_position = 'SUP'
        elif prefer_position == 'BOTTOM':
            prefer_position = 'ADC'
        match_average_data = {'kda': round(kda / 50, 2),
                              'kills': round(kills / 50, 1),
                              'deaths': round(deaths / 50, 1),
                              'assists': round(assists / 50, 1),
                              'prefer_position': {prefer_position: position_rate}
                              }
        return match_average_data


@ app.get("/user/{summoner_name}")
async def get_summoner(summoner_name: str):
    summoner_info = {}
    summoner_basic_info = await get_summoner_basic_info(summoner_name)
    print(summoner_basic_info)
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
