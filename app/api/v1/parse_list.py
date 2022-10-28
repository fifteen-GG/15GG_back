from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud
from app.api.deps import get_db

import urllib
import pandas as pd
from bs4 import BeautifulSoup
import grequests

router = APIRouter()


def get_parse_list():
    requests_list = [
        grequests.post('https://fow.kr/neo_ranking.php', data={'start': page})
        for page in range(1, 5001, 50)
    ]
    user_list = []

    for response in grequests.map(requests_list):
        for html in BeautifulSoup(response.text, features='html.parser').findAll('a'):
            user_list.append(html.text)

    print(user_list)

    requests_list = [
        grequests.get('https://fow.kr/find/' + urllib.parse.quote(name))
        for name in user_list
    ]

    game_list = set()

    for response in grequests.map(requests_list):
        for html in BeautifulSoup(response.content, features='html.parser', from_encoding='utf-8'):
            try:
                table = html.find(
                    'table', {'class': 'tablesorter table_recent'}).find_all('tbody')
                for tbody in table:
                    for tr in tbody.find_all('tr'):
                        info = tr.find_all('td', {'class': 'recent_td'})
                        if info[2].text == '랭크':
                            game_list.add('KR-'+info[-1]['onclick'][11: 21])
            except:
                pass

    pd.DataFrame(list(game_list), columns=['game_id']).to_csv(
        'game_list.csv', index=False)
    return game_list


@router.get('', response_model=List[schemas.ParseMatch])
def parse_list(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):

    parse_list = crud.parseMatch.get_multi(db, skip=skip, limit=limit)
    # status가 false인 match만 뽑아서 return
    return parse_list


@router.post('')
def parse_list_post(db: Session = Depends(get_db)):
    parse_list = get_parse_list()
    for match_id in parse_list:
        # db에 있는지 확인
        # 있다면 skip, 없다면 post
        print(match_id)
    return
