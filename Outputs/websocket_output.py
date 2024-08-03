from DataFormat.datatypes_helper import wrap_socket_message_with_metadata
from base_keys import WEBSOCKET_DATATYPE, WEBSOCKET_MESSAGE
from base_component import BaseComponent
from Websocket import socket_server
from base_keys import WEBSOCKET_CLIENT_TYPE


class WebsocketOutput(BaseComponent):
    def __init__(self, name) -> None:
        super().__init__(name)

    def send(self, raw_data):
        websocket_message = raw_data.get(WEBSOCKET_MESSAGE)
        websocket_datatype = raw_data.get(WEBSOCKET_DATATYPE)  # can be None
        websocket_client_type = raw_data.get(WEBSOCKET_CLIENT_TYPE)

        output_data = wrap_socket_message_with_metadata(websocket_message, websocket_datatype)

        socket_server.send_data(output_data, websocket_client_type)
