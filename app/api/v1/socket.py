import asyncio
import json
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

router = APIRouter()


async def echo_message(websocket: WebSocket):
    data = await websocket.receive_text()
    await websocket.send_text(f"Message text was: {data}")


async def send_result(websocket: WebSocket):
    with open('./app/assets/sample_result.json', encoding='UTF-8') as file:
        data = json.load(file)
        timestamp, index = 0, 0
        while True:
            timestamp += 1
            await asyncio.sleep(1)
            try:
                if int(data[index]['timestamp']) == timestamp:
                    await websocket.send_json(data[index])
                    index += 1
            except IndexError:
                break


@router.websocket('')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            echo_message_task = asyncio.create_task(echo_message(websocket))
            send_time_task = asyncio.create_task(send_result(websocket))
            done, pending = await asyncio.wait(
                {echo_message_task, send_time_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect:
        await websocket.close()
