from quart import Blueprint, redirect, request, Response, jsonify, websocket
from quart.wrappers.request import Request
import asyncio
import aiohttp
import websockets
from common import MongoConnector
from http import HTTPStatus
import os

blueprint = Blueprint('routes', __name__)

collection = MongoConnector()

async def serverToClient(ws_client, ws_server):
    async for message in ws_server:
        await ws_client.send(message)

async def getTargetServiceUrl(req: Request, service: str = "THEIA_BACKEND"): 
    service_host = os.getenv(service.upper() + "_SERVICE_HOST")
    if not service_host:
            service_host = "atcvt"
    port = os.getenv(service.upper() + "_SERVICE_PORT")
    if not port:
        port = "7000"
    print(req.host, req.host_url)
    targetUrl = req.url.replace(req.host, service_host+":"+port)
    return targetUrl

async def getTargetPodUrl(pipeline_uuid: str, req: Response, service: str="THEIA_BACKEND"):
    pod_ip = collection.read_one(pipeline_uuid)['container_host_ip']
    port = os.getenv(service.upper() + "_CONTAINER_PORT")
    if not port:
        port = "7000"
    targetUrl = req.url.replace(req.host, pod_ip+":"+port)
    return targetUrl

async def fetch_post(session: aiohttp.ClientSession, targetUrl: str, request_data):
    async with session.post(targetUrl, data=request_data) as resp:
                # response = await resp.json()
        return await resp.text()


async def fetch_get(session: aiohttp.ClientSession, targetUrl: str):
    async with session.get(targetUrl) as resp:
                # response = await resp.json()
        return await resp.text()


async def fetch_put(session: aiohttp.ClientSession, targetUrl: str, request_data):
    async with session.put(targetUrl, data=request_data) as resp:
                # response = await resp.json()
        return await resp.text()



@blueprint.route('/pipelines', methods=['GET', 'POST'])
async def pipelines_handler():
    
    if request.method == "GET":
        return collection.read_all()
    elif request.method == "POST":

        targetUrl = await getTargetServiceUrl(request)

        request_data = await request.get_data()
        async with aiohttp.ClientSession() as session:
            response = await fetch_post(session=session, targetUrl=targetUrl, request_data=request_data)
                
        return response

@blueprint.route('/pipelines/<pipeline_uuid>', methods=['GET', 'PUT'])
async def pipeline_uuid_handler(pipeline_uuid: str):
    targetUrl = await getTargetPodUrl(pipeline_uuid, request)
    if request.method == "GET":
        async with aiohttp.ClientSession() as session:
            response = await fetch_get(session=session, targetUrl=targetUrl)
        return response
    elif request.method == "PUT":
        request_data = await request.get_data()
        async with aiohttp.ClientSession() as session:
            response = await fetch_put(session=session, targetUrl=targetUrl, request_data=request_data)
                
        return response

@blueprint.route('/pipelines/<pipeline_uuid>/state', methods=['PUT'])
async def pipeline_state_handler(pipeline_uuid: str):
    assert request.method == 'PUT'
    targetUrl = await getTargetPodUrl(pipeline_uuid, request)
    async with aiohttp.ClientSession() as session:
        return await fetch_put(session=session, targetUrl=targetUrl, request_data=None)

@blueprint.route('/pipelines/<pipeline_uuid>/elements')
async def pipeline_element_handler(pipeline_uuid: str):
    targetUrl = await getTargetPodUrl(pipeline_uuid, request)
    async with aiohttp.ClientSession() as session:
        return await fetch_get(session=session, targetUrl=targetUrl)

@blueprint.route('/pipelines/<pipeline_uuid>/elements/<element_name>/pads')
async def pipeline_element_pads_handler(pipeline_uuid: str, element_name: str):
    targetUrl = await getTargetPodUrl(pipeline_uuid, request)
    async with aiohttp.ClientSession() as session:
        return await fetch_get(session=session, targetUrl=targetUrl)

@blueprint.websocket('/pipelines/<pipeline_uuid>/elements/<element_name>/pads/<pad_name>/probe')
async def ws(pipeline_uuid: str, element_name: str, pad_name: str):
    
    targetUrl = await getTargetPodUrl(pipeline_uuid, websocket)
    print(targetUrl)
    async with websockets.connect(targetUrl) as ws_server:
        taskB = asyncio.create_task(serverToClient(websocket, ws_server))
        await taskB


# @blueprint.route('/test')
# async def test():

#     url=request.url.replace(request.url, 'http://atcvt:7000/pipelines/79235f46-4b66-11ec-bc84-0242ac130002/elements')
#     print(url)
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as resp:
#             # response = await resp.json()
#             response = await resp.text()
#             print(type(response))

#     return response


# @blueprint.websocket('/ws')
# async def ws():
#     url = "ws://atcvt:7000/wst"
#     async with websockets.connect(url) as ws_server:
#         taskB = asyncio.create_task(serverToClient(websocket, ws_server))
#         await taskB