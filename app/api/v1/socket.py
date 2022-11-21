import asyncio
import json
import random
import functools
import aio_pika
import aio_pika.abc
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from app import crud
from app.database.session import SessionLocal

router = APIRouter()


async def block_io(websocket: WebSocket):
    _ = await websocket.receive_text()


async def on_message(message: aio_pika.IncomingMessage, websocket: WebSocket):
    async with message.process():
        await websocket.send_json(json.loads(
            message.body.decode('UTF-8').replace("'", "\"")))


async def analyze(
        websocket: WebSocket, exchange: aio_pika.Exchange,
        match_id: str, result: dict):
    new_data: dict = await websocket.receive_json()
    # TODO: Caculate win rate from AI model
    new_data['blue_team_win_rate'] = round(random.uniform(0, 1), 3)
    result['match_data'].append(new_data)
    response = bytes(json.dumps(result, ensure_ascii=False), 'UTF-8')
    response = aio_pika.Message(
        response, content_encoding='UTF-8')
    await exchange.publish(message=response, routing_key=match_id)


async def create_exchange(websocket: WebSocket, connection):
    data = await websocket.receive_text()
    channel = connection.channel()
    channel.exchange_declare(
        exchange='direct_logs', exchange_type='direct')
    tmp_queue = channel.queue_declare(queue='', exclusive=True)
    queue_name = tmp_queue.method.queue
    channel.queue_bind(exchange='direct_logs',
                       queue=queue_name, routing_key=data)
    print('Exchange declared')
    print(data)


@router.websocket('/analyze')
async def analyze_game(websocket: WebSocket):
    '''
    Websocket endpoint for analyzing game.
    When a DataNashor client connects to this endpoint,
    it will create a new exchange and bind it to the match_id.

    All the match data parsed from DataNashor will be passed to the AI model,
    the the result will be broadcasted to the clients connected.
    '''
    await websocket.accept()
    try:
        match_id = await websocket.receive_text()
        result = {'match_id': match_id, 'match_data': []}
        connection = await aio_pika.connect('amqp://guest:guest@localhost/')
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            name='game_logs', type='direct')
        print(f'Exchange {match_id} declared')
        while True:
            producer_task = asyncio.create_task(
                analyze(websocket, exchange, match_id, result))
            done, pending = await asyncio.wait(
                {producer_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect:
        print(result)
        await connection.close()


@router.websocket('/match/{match_id}')
async def get_match_data(websocket: WebSocket, match_id: str):
    '''
    Websocket endpoint for getting match data.
    It will listen to the brodacast messages of match data
    from the exchange bound to the match_id.
    '''
    await websocket.accept()
    try:
        connection = await aio_pika.connect('amqp://guest:guest@localhost/')
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            name='game_logs', type='direct')
        queue = await channel.declare_queue(name='', exclusive=True)
        await queue.bind(exchange, routing_key=match_id)

        while True:
            consume = queue.consume(functools.partial(
                on_message, websocket=websocket))

            block_io_task = asyncio.create_task(block_io(websocket))
            consumer_task = asyncio.create_task(consume)

            done, pending = await asyncio.wait(
                {block_io_task, consumer_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect:
        await connection.close()


@router.websocket('/wait/{code}')
async def wait_analyis(websocket: WebSocket, code: str):
    '''
    Websocket endpoint that waits for a match analysis to start.
    '''
    await websocket.accept()
    db = SessionLocal()
    validated = False
    try:
        while True:
            try:
                code_obj = crud.code.get(db, code).value
                await websocket.send_text(code_obj)
                validated = True
            except AttributeError:
                if not validated:
                    await websocket.send_text('Code not found')
                    raise WebSocketDisconnect
                else:
                    await websocket.send_text('Code validated')
                    raise WebSocketDisconnect
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await websocket.close()
