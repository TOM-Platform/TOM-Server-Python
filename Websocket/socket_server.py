import asyncio
import threading
import time
from asyncio import Queue
from urllib.parse import urlparse, parse_qs
import websockets
from Utilities import environment_utility, logging_utility
from base_keys import WEBSOCKET_CLIENT_TYPE

_SERVER_IP = environment_utility.get_env_variable_or_default("SERVER_IP", "")
_SERVER_PORT = environment_utility.get_env_int("SERVER_PORT")

_CONNECTIONS = set()
_rx_queue = Queue()
loop = None

_logger = logging_utility.setup_logger(__name__)


# references: https://websockets.readthedocs.io/en/stable/reference/server.html , https://pypi.org/project/websockets/
async def receive_data_from_websocket(websocket):
    global _rx_queue, _CONNECTIONS

    _CONNECTIONS.add(websocket)
    _logger.debug("New websocket connection:: total: {num_connections}", num_connections=len(_CONNECTIONS))

    try:
        headers = websocket.request_headers
        websocket_client_type = headers.get(WEBSOCKET_CLIENT_TYPE)

        if websocket_client_type is None:
            query_params = parse_qs(urlparse(websocket.path).query)
            websocket_client_type = query_params.get("websocket_client_type", [None])[0]

        async for rx_data in websocket:
            _rx_queue.put_nowait(rx_data)
            current_time = int(time.time() * 1000)
            _logger.debug("{curr_time}, received, websocket_client_type: {type}", curr_time=current_time,
                          type=websocket_client_type)

    except Exception:
        _logger.exception("Error receiving data from websocket")
    finally:
        _CONNECTIONS.remove(websocket)
        _logger.warn("Websocket disconnection total: {num_connections}", num_connections=len(_CONNECTIONS))


# Broadcast message to all websocket clients.
def broadcastmsg(msg):
    websockets.broadcast(_CONNECTIONS, msg)


async def ws_main():
    async with websockets.serve(receive_data_from_websocket, _SERVER_IP, _SERVER_PORT):
        await asyncio.Future()  # run forever


async def main():
    global loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError as e:
        _logger.exception(e)
    websocket_task = asyncio.create_task(ws_main())
    await asyncio.gather(websocket_task)


def start_server():
    asyncio.run(main())


def stop_server():
    pass


async def send_data_to_websockets(data, websocket_client_type=None):
    global _CONNECTIONS

    exclude_list = set()
    for _websocket in _CONNECTIONS:
        try:
            headers = _websocket.request_headers
            curr_client_type = headers.get(WEBSOCKET_CLIENT_TYPE)

            if curr_client_type is None:
                query_params = parse_qs(urlparse(_websocket.path).query)
                curr_client_type = query_params.get("websocket_client_type", [None])[0]

            if (websocket_client_type is not None) and (curr_client_type != websocket_client_type):
                continue

            await _websocket.send(data)
            current_time = int(time.time() * 1000)
            _logger.debug("{current_time}, sent, websocket_client_type: {curr_client_type}", current_time=current_time,
                          curr_client_type=curr_client_type)
        except Exception:
            _logger.exception("Error sending data to websocket")
            exclude_list.add(_websocket)
    if isinstance(data, str):
        _logger.debug("Sent data: {data}", data=data)
    else:
        _logger.debug("Sent data: {len} bytes", len=len(data))
        _CONNECTIONS -= exclude_list


def send_data(data, websocket_client_type=None):
    global loop
    if loop and loop.is_running():
        _logger.debug("loop is running")
        asyncio.run_coroutine_threadsafe(send_data_to_websockets(data, websocket_client_type), loop)
    else:
        asyncio.run(send_data_to_websockets(data, websocket_client_type))
        _logger.warning("loop is none or loop is not running")


def receive_data():
    global _rx_queue
    if _rx_queue.empty():
        return None

    _logger.debug("rx_size: {queue_size}", queue_size=_rx_queue.qsize())

    return _rx_queue.get_nowait()


server_thread = None


def start_server_threaded():
    global server_thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()


def stop_server_threaded():
    global server_thread
    stop_server()

    server_thread.join(timeout=2)
