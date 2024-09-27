from google.protobuf import json_format as protobuf_json_format

import base_keys
from base_component import BaseComponent
from DataFormat import datatypes_helper
from Websocket import socket_server
from Utilities import time_utility, logging_utility

_NO_DATA_SLEEP_SECONDS = 0.05

_logger = logging_utility.setup_logger(__name__)


class WebsocketWidget(BaseComponent):
    """
    Sends a message in the following format (only to components which have been indicated in DataFormat/datatypes.json):
    {
        "websocket_message": "<protobuf message sent through websocket server, in dictionary format>",
        "websocket_datatype": "<protobuf datatype key of the websocket_message>"
    }
    """

    def start(self):
        socket_server.start_server_threaded()
        _logger.info("Listening on Websocket Widget")
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        while True:
            data = socket_server.receive_data()
            if not data:
                time_utility.sleep_seconds(_NO_DATA_SLEEP_SECONDS)
                continue

            data_type_key, data = datatypes_helper.decode_websocket_data(data)

            # If error while decoding, decoder.decode returns (None, None)
            if not data_type_key:
                continue

            # To check for which service requires the specific message type, we convert the protobuf message to dict
            data = protobuf_json_format.MessageToDict(data, preserving_proto_field_name=True)

            super().send_to_component(websocket_message=data, websocket_datatype=data_type_key)

            # HACK: Allow other threads to run
            time_utility.sleep_seconds(_NO_DATA_SLEEP_SECONDS)
