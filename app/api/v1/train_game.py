import asyncio
from typing import List

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app import schemas, crud
from app.api.deps import get_db

import urllib
from bs4 import BeautifulSoup
import httpx

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from app.database.session import SessionLocal

import os

router = APIRouter()


async def get_train_game():
    user_list = []
    async with httpx.AsyncClient() as client:
        requests_list = [
            client.post('https://fow.kr/neo_ranking.php', data={'start': page})
            for page in range(1, 5001, 50)
        ]
        result_list = await asyncio.gather(*requests_list)
        for result in result_list:
            for html in BeautifulSoup(result.text, features='html.parser').findAll('a'):
                user_list.append(html.text)

    async with httpx.AsyncClient() as client:
        requests_list = [
            client.get('https://fow.kr/find/' + urllib.parse.quote(name))
            for name in user_list
        ]
        result_list = await asyncio.gather(*requests_list)
        # riot api로 바꿀 수 있으면 바꾸기

        game_list = set()
        for result in result_list:
            for html in BeautifulSoup(result.content, features='html.parser', from_encoding='utf-8'):
                try:
                    table = html.find(
                        'table', {'class': 'tablesorter table_recent'}).find_all('tbody')
                    for tbody in table:
                        for tr in tbody.find_all('tr'):
                            info = tr.find_all('td', {'class': 'recent_td'})
                            if info[2].text == '랭크':
                                game_list.add(
                                    'KR-'+info[-1]['onclick'][11: 21])
                except:
                    pass

    return game_list


async def train_game_post(db: Session = Depends(get_db)):
    db: Session = SessionLocal()
    train_game_list = await get_train_game()
    # crud.train_game.create_train_game(db, train_game_list)
    query = ""
    for match_id in train_game_list:
        if query == "":
            query = f"('{match_id}', false)"
        else:
            query += f",('{match_id}', false)"
    db.execute(
        f"INSERT INTO train_game (match_id, is_parsed) VALUES {query} ON CONFLICT (match_id) DO NOTHING")
    db.commit()
    return


@ router.get('', response_model=List[schemas.TrainGame])
def train_game_get(db: Session = Depends(get_db)):
    train_game_list = crud.train_game.get_train_game(db)

    return train_game_list


@ router.post('/upload_json')
async def upload_json(result_file: UploadFile, meta_file: UploadFile, db: Session = Depends(get_db)):
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None

    SCOPES = 'https://www.googleapis.com/auth/drive.file'
    store = file.Storage('storage.json')
    creds = store.get()

    if not creds or creds.invalid:
        print("make new storage data file ")
        flow = client.flow_from_clientsecrets(
            'client_secret_drive.json', SCOPES)
        creds = tools.run_flow(flow, store, flags) \
            if flags else tools.run(flow, store)

    DRIVE = build('drive', 'v3', http=creds.authorize(Http()))

    with open(result_file.filename, 'wb') as f:
        content = await result_file.read()
        f.write(content)
        f.close()

    with open(meta_file.filename, 'wb') as f:
        content = await meta_file.read()
        f.write(content)
        f.close()

    FILES = [result_file.filename, meta_file.filename]
    for file_title in FILES:
        metadata = {'name': file_title, 'mimeType': None}
        res = DRIVE.files().create(body=metadata, media_body=file_title).execute()
        if res and file_title.split('_')[0] == 'result':
            print('Uploaded "%s" (%s)' % (file_title, res['mimeType']))
            crud.train_game.update_is_parsed(db, file_title)
        os.remove(f'./{file_title}')
