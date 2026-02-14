import joblib
from pathlib import Path
from fastapi import FastAPI, WebSocket
import asyncio
from connection_manager import ConnectionManager

model_path = Path(__file__).resolve().parent.parent.parent / 'model' / 'model.pkl'
model = joblib.load(model_path)

# TODO: Use the model to generate the game prediction

home_votes = 0
away_votes = 0
home_voters = set()
away_voters = set()
GAME_STATE = {}

manager = ConnectionManager()
broadcast_queue = asyncio.Queue()

# Poll function

async def broadcaster():
    while True:
        message = await broadcast_queue.get()
        await manager.broadcast(message)

async def lifespan(app: FastAPI):
    task = asyncio.create_task(broadcaster())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    manager.connect(websocket)
    while True:
        # TODO: listen for client messages and add to mesage queue
        pass
