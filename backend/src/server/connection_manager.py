from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active = set()

    def connect(self, websocket: WebSocket):
        self.active.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active.discard(websocket)

    async def broadcast(self, message: dict):
        connections = self.active.copy()
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                self.active.discard(ws)

        