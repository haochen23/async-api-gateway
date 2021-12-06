import json
import asyncio
from pprint import pp

from quart import Quart, websocket, render_template, request, send_from_directory
from quart import g
import websockets
import time

from routes import blueprint

app = Quart(__name__)
# REMOTE_URL = "ws://atcvt:7000/wst"

async def serverToClient(ws_client, ws_server):
    async for message in ws_server:
        await ws_client.send(message)

@app.route("/")
async def index():
    return await send_from_directory('static', "index.html")

app.register_blueprint(blueprint)

app.run(use_reloader=True, host="0.0.0.0", port=9000)
