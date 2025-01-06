import signal
from urllib.parse import urlparse, parse_qs

import asyncio
import websockets

from google.protobuf import json_format as protobuf_json_format

from base_component import BaseComponent

from DataFormat.datatypes_helper import wrap_socket_message_with_metadata
from DataFormat import datatypes_helper

from Utilities import logging_utility, environment_utility

import base_keys
from base_keys import WEBSOCKET_DATATYPE, WEBSOCKET_MESSAGE, WEBSOCKET_CLIENT_TYPE

_logger = logging_utility.setup_logger(__name__)

class WebsocketWidget(BaseComponent):
    """
    Sends a message in the following format (only to components which have been indicated in DataFormat/datatypes.json):
    {
        "websocket_message": "<protobuf message sent through websocket server, in dictionary format>",
        "websocket_datatype": "<protobuf datatype key of the websocket_message>"
    }
    """

    # All websocket connections
    connections = set()

    # Client Type (refer to DeveloperGuide.md on types -- Unity, WearOS, Dashboard)
    typed_connections = {
        base_keys.UNITY_CLIENT: set(),
        base_keys.WEAROS_CLIENT: set(),
        base_keys.DASHBOARD_CLIENT: set()
    }

    # Send queue for broadcast messages
    tx_queue = asyncio.Queue()

    typed_tx_queues = {
        base_keys.UNITY_CLIENT: asyncio.Queue(),
        base_keys.WEAROS_CLIENT: asyncio.Queue(),
        base_keys.DASHBOARD_CLIENT: asyncio.Queue()
    }


    # Consumer Handler (Handles incoming messages)

    async def _consume(self, recvdata):
        data_type_key, data = datatypes_helper.decode_websocket_data(recvdata)

        # If error while decoding, decoder.decode returns (None, None)
        if not data_type_key:
            return

        # To check for which service requires the specific message type, we convert the protobuf message to dict
        dictdata = protobuf_json_format.MessageToDict(data, preserving_proto_field_name=True)

        # Included original websocket data for handlers that use its original format.
        super().send_to_component(websocket_message=dictdata, websocket_datatype=data_type_key, websocket_data=data)

    def _decode_ws_client_type(self, wsheaders, path):
        # Check from the websocket headers first
        client_type = wsheaders.get(WEBSOCKET_CLIENT_TYPE, None)
        if client_type is not None:
            return client_type

        # If not, check from the URL
        result = urlparse(path)
        if result.query:
            qs = parse_qs(result.query)
            params = qs.get(WEBSOCKET_CLIENT_TYPE, None)
            if params is not None and len(params) > 0:
                return params[0]
        return None

    async def _consumer_handler(self, websocket):
        """
        Handles new websocket connections to this server.
        """
        ws_client_type = self._decode_ws_client_type(websocket.request.headers, websocket.request.path)
        print("Client Type: ", ws_client_type)
        _logger.debug("New websocket connection:: total: {num_connections}", num_connections=len(self.connections))

        # Save connections
        if ws_client_type == base_keys.DASHBOARD_CLIENT:
            self.typed_connections[base_keys.DASHBOARD_CLIENT].add(websocket)
        elif ws_client_type == base_keys.UNITY_CLIENT:
            self.typed_connections[base_keys.UNITY_CLIENT].add(websocket)
        elif ws_client_type == base_keys.WEAROS_CLIENT:
            self.typed_connections[base_keys.WEAROS_CLIENT].add(websocket)

        # Add to all connections. 
        self.connections.add(websocket)

        # Loop and Process message received from this connection
        try:
            async for message in websocket:
                await self._consume(message)
        except Exception:
            _logger.exception('Error receiving data from websocket')
        finally:
            # Connection closed. ---

            # Remove from all connections. 
            self.connections.remove(websocket)

            # Remove from typed connections
            if ws_client_type == base_keys.DASHBOARD_CLIENT:
                self.typed_connections[base_keys.DASHBOARD_CLIENT].remove(websocket)
            elif ws_client_type == base_keys.UNITY_CLIENT:
                self.typed_connections[base_keys.UNITY_CLIENT].remove(websocket)
            elif ws_client_type == base_keys.WEAROS_CLIENT:
                self.typed_connections[base_keys.WEAROS_CLIENT].remove(websocket)

            _logger.debug("Websocket disconnection total: {num_connections}", num_connections=len(self.connections))


    # Producer Handlers. (for sending message to client)

    def _send_to_wsconections_message(self, wsconnections, raw_data):
        """
        Broadcasts messages to all connections.
        (Based on the websocket_output codes) 
        """
        if len(wsconnections) > 0:
            # websockets.broadcast(self.connections, msg)
            websocket_datatype = raw_data.get(WEBSOCKET_DATATYPE)
            websocket_message = raw_data.get(WEBSOCKET_MESSAGE)
            if websocket_message is not None:
                output_data = wrap_socket_message_with_metadata(websocket_message, websocket_datatype)
                websockets.broadcast(self.connections, output_data)

    async def _process_send_to_all_events(self):
        while True:
            message = await self.tx_queue.get()
            self._send_to_wsconections_message(self.connections, message)

    async def _process_send_to_dashboard_events(self):
        q = self.typed_tx_queues[base_keys.DASHBOARD_CLIENT]
        wsconns = self.typed_connections[base_keys.DASHBOARD_CLIENT]
        while True:
            message = await q.get()
            self._send_to_wsconections_message(wsconns, message)

    async def _process_send_to_unity_events(self):
        q = self.typed_tx_queues[base_keys.UNITY_CLIENT]
        wsconns = self.typed_connections[base_keys.UNITY_CLIENT]
        while True:
            message = await q.get()
            self._send_to_wsconections_message(wsconns, message)

    async def _process_send_to_wearos_events(self):
        q = self.typed_tx_queues[base_keys.WEAROS_CLIENT]
        wsconns = self.typed_connections[base_keys.WEAROS_CLIENT]
        while True:
            message = await q.get()
            self._send_to_wsconections_message(wsconns, message)


    # Public APIs
    def output_send(self, raw_data):
        """
        (Public API) External for sending data to the next component. 
        (Puts data into the send queue for processing)
        """
        # Checks the intended target and put to the right queue
        target_client_type = raw_data.get(WEBSOCKET_CLIENT_TYPE)
        if target_client_type is None:
            # Send to all connections if no target client type
            if self.tx_queue is not None:
                self.tx_queue.put_nowait(raw_data)
        else:
            typed_queue = self.typed_tx_queues.get(target_client_type, None)
            if typed_queue is not None:
                typed_queue.put_nowait(raw_data)


    async def start(self):
        _SERVER_IP = environment_utility.get_env_variable_or_default("SERVER_IP", "")
        _SERVER_PORT = environment_utility.get_env_int("SERVER_PORT")

        # Set the stop condition when receiving SIGTERM.
        loop = asyncio.get_running_loop()
        stop = loop.create_future()
        # TODO: Commented as add_signal_handler is not supported in Windows
        # loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

        _logger.info("Starting websocket at port {port}", port=_SERVER_PORT)
        async with websockets.serve(self._consumer_handler, _SERVER_IP, _SERVER_PORT):
            _logger.info("Listening on Websocket Widget")
            super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

            # Await until the server is stopped.
            await asyncio.gather(
                self._process_send_to_all_events(),
                self._process_send_to_dashboard_events(),
                self._process_send_to_unity_events(),
                self._process_send_to_wearos_events(),
            )

            # Server stopped. 
            print("Stopping websocket server")
            super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)

