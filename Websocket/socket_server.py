import asyncio
import threading
import time
from queue import Queue  # Using standard Queue for thread-safety
from urllib.parse import urlparse, parse_qs
import websockets
from Utilities import environment_utility, logging_utility
from base_keys import WEBSOCKET_CLIENT_TYPE

_SERVER_IP = environment_utility.get_env_variable_or_default("SERVER_IP", "")
_SERVER_PORT = environment_utility.get_env_int("SERVER_PORT")

SERVER_STOP_TIMEOUT_SECONDS = 2
ASYNCIO_SLEEP_SECONDS = 0.1

_CONNECTIONS = set()
_rx_queue = Queue()  # Standard Queue for thread-safety

_running = False
_loop = None
_server_thread = None

_logger = logging_utility.setup_logger(__name__)


def _get_client_type(websocket):
    """Extract client type from headers or query parameters."""
    headers = websocket.request_headers
    client_type = headers.get(WEBSOCKET_CLIENT_TYPE)

    if client_type is None:
        query_params = parse_qs(urlparse(websocket.path).query)
        client_type = query_params.get(WEBSOCKET_CLIENT_TYPE, [None])[0]

    return client_type


# references: https://websockets.readthedocs.io/en/stable/reference/server.html , https://pypi.org/project/websockets/
async def receive_data_from_websocket(websocket):
    global _rx_queue, _CONNECTIONS

    _CONNECTIONS.add(websocket)
    _logger.debug("New websocket connection:: total: {num_connections}", num_connections=len(_CONNECTIONS))

    try:
        websocket_client_type = _get_client_type(websocket)

        async for rx_data in websocket:
            _rx_queue.put(rx_data)  # Using standard Queue's put method
            _logger.debug("[RX] websocket_client_type: {type}",
                          curr_time=int(time.time() * 1000),
                          type=websocket_client_type)

    except websockets.exceptions.ConnectionClosed:
        _logger.info("WebSocket connection closed normally")
    except Exception:
        _logger.exception("Error receiving data from websocket")
    finally:
        _CONNECTIONS.remove(websocket)
        _logger.warning("Websocket disconnection total: {num_connections}", num_connections=len(_CONNECTIONS))


# Broadcast message to all websocket clients.
def broadcastmsg(msg):
    _logger.debug("Broadcasting message to all clients: {msg}", msg=msg)
    if _CONNECTIONS:
        websockets.broadcast(_CONNECTIONS, msg)


async def ws_server(stop_event):
    """Run the WebSocket server until the stop event is set."""
    global _CONNECTIONS

    async with websockets.serve(receive_data_from_websocket, _SERVER_IP, _SERVER_PORT):
        _logger.info("WebSocket server started on {ip}:{port}", ip=_SERVER_IP, port=_SERVER_PORT)
        # Wait until the stop event is set
        while not stop_event.is_set():
            try:
                await asyncio.sleep(ASYNCIO_SLEEP_SECONDS)
            except asyncio.CancelledError:
                break

    # Close all connections when exiting
    close_tasks = [ws.close() for ws in _CONNECTIONS]
    if close_tasks:
        await asyncio.gather(*close_tasks, return_exceptions=True)
    _CONNECTIONS.clear()
    _logger.info("WebSocket server stopped")


async def run_server(stop_event):
    """Main entry point for the asyncio server."""
    global _loop

    try:
        _loop = asyncio.get_running_loop()
        await ws_server(stop_event)
    except asyncio.CancelledError:
        _logger.info("Server task cancelled")
    except Exception:
        _logger.exception("Error in WebSocket server")


def server_thread_function():
    """Function to run in the server thread."""
    global _running, _server_task

    stop_event = asyncio.Event()

    try:
        asyncio.run(run_server(stop_event))
    except Exception:
        _logger.exception("Unhandled exception in server thread")
    finally:
        _running = False
        _logger.info("Server thread exited")


def start_server():
    """Legacy function - not used, kept for compatibility."""
    server_thread_function()


def stop_server():
    """Signal the server to stop."""
    global _running, _loop, _server_task

    if not _running:
        return

    _running = False

    # Cancel any remaining tasks if we have a loop
    if _loop and _loop.is_running():
        for task in asyncio.all_tasks(_loop):
            task.cancel()
        _logger.info("WebSocket server tasks cancelled")


async def send_data_to_websockets(data, websocket_client_type=None):
    """Send data to matching WebSocket clients."""
    global _CONNECTIONS

    if not _CONNECTIONS:
        return

    exclude_list = set()
    for ws in _CONNECTIONS:
        try:
            curr_client_type = _get_client_type(ws)

            if (websocket_client_type is not None) and (curr_client_type != websocket_client_type):
                _logger.warning("Client type mismatch: {curr_client_type} != {websocket_client_type}",
                                curr_client_type=curr_client_type, websocket_client_type=websocket_client_type)
                continue

            await ws.send(data)
            _logger.debug("[TX] websocket_client_type: {curr_client_type}",
                          curr_client_type=curr_client_type)
        except Exception:
            _logger.exception("Error sending data to websocket")
            exclude_list.add(ws)

    # Remove failed connections
    if exclude_list:
        _CONNECTIONS -= exclude_list

    if isinstance(data, str):
        _logger.debug("Sent data: {data}", data=data)
    else:
        _logger.debug("Sent data: {n} bytes", n=len(data))


def send_data(data, websocket_client_type=None):
    """Send data to WebSocket clients, can be called from any thread."""
    global _loop, _running

    if not _running:
        _logger.warning("Cannot send data: Server not running")
        return

    if _loop and _loop.is_running():
        asyncio.run_coroutine_threadsafe(
            send_data_to_websockets(data, websocket_client_type),
            _loop
        )
    else:
        # Fallback - this is not ideal but maintained for compatibility
        _logger.warning("Using asyncio.run for sending (less efficient)")
        asyncio.run(send_data_to_websockets(data, websocket_client_type))


def receive_data():
    """Receive data from the queue, non-blocking."""
    global _rx_queue

    if _rx_queue.empty():
        return None

    _logger.debug("rx_size: {queue_size}", queue_size=_rx_queue.qsize())

    try:
        return _rx_queue.get_nowait()
    except Exception:
        return None


def start_server_threaded():
    """Start the WebSocket server in a separate thread."""
    global _server_thread, _running

    if _running:
        _logger.info("WebSocket server already running")
        return

    _running = True
    _server_thread = threading.Thread(target=server_thread_function, daemon=True)
    _server_thread.start()
    _logger.info("WebSocket server started in a thread")


def stop_server_threaded():
    """Stop the WebSocket server thread."""
    global _server_thread, _running

    if not _running:
        return

    stop_server()

    if _server_thread and _server_thread.is_alive():
        _server_thread.join(timeout=SERVER_STOP_TIMEOUT_SECONDS)
        _logger.info("WebSocket server thread joined")
