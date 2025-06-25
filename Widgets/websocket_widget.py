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
    Sends a message in the following format (only to components derived from BaseComponent whose values are listed
    in `SUPPORTED_DATATYPES`):
    {
        "websocket_datatype": "<Integer value representing the protobuf message type (the `key` attribute in
        DataFormat/DataTypes.json)>",
        "websocket_message": "<Protobuf message sent through the WebSocket server, in dictionary format>",
    }
    """

    def start(self):
        socket_server.start_server_threaded()
        _logger.info("Listening on Websocket Widget")
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        try:
            self._process_messages()
        except KeyboardInterrupt:
            _logger.info("WebsocketWidget stopped by user")
        except Exception:
            _logger.exception("Error in WebsocketWidget")
        finally:
            socket_server.stop_server_threaded()

    def _process_messages(self):
        """Process incoming websocket messages in a loop."""
        while True:
            data = socket_server.receive_data()
            if not data:
                time_utility.sleep_seconds(_NO_DATA_SLEEP_SECONDS)
                continue

            data_type_key, data = datatypes_helper.decode_websocket_data(data)

            # If error while decoding, decoder.decode returns (None, None)
            if not data_type_key:
                _logger.warning("Failed to decode websocket data")
                continue

            # To check for which service requires the specific message type, we convert the protobuf message to dict
            data_dict = protobuf_json_format.MessageToDict(data, preserving_proto_field_name=True)

            super().send_to_component(websocket_message=data_dict, websocket_datatype=data_type_key)

            # Allow other threads to run
            time_utility.sleep_seconds(_NO_DATA_SLEEP_SECONDS)
