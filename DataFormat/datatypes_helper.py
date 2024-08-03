import importlib
import os

from google.protobuf import json_format
from google.protobuf.message import DecodeError

from DataFormat.ProtoFiles.Common import socket_data_pb2
from Utilities import file_utility, logging_utility
from Utilities.file_utility import get_project_root

_PROTO_FILE_IMPORT_PATH = "DataFormat.ProtoFiles"
_DATA_TYPE_FILE_PATH = os.path.join(get_project_root(), "DataFormat", "DataTypes.json")

## DataType JSON Keys
DATA_TYPE_JSON_VAL_KEY = "key"
DATA_TYPE_JSON_VAL_PROTO_FILE = "proto_file"
DATA_TYPE_JSON_VAL_COMPONENTS = "components"

_logger = logging_utility.setup_logger(__name__)

##########################################################
################# Internal Functions #####################
##########################################################


def _get_data_type_json():
    """
    :return: DataTypes in JSON format

    Example:
    {"EXERCISE_WEAR_OS_DATA": {
        "key": 1000,
        "proto_file": "exercise_wear_os_data_pb2.py",
        "components": [
            "service:running"
        ]
    },}
    """
    return file_utility.read_json_file(_DATA_TYPE_FILE_PATH)


def _get_data_type_to_key_mapping():
    """
    :return: the map with { "EXERCISE_WEAR_OS_DATA": 1000, ... }
    """
    data_type_key_map = {}

    for key, val in DATATYPE_JSON.items():
        data_type_key_map[key] = val[DATA_TYPE_JSON_VAL_KEY]

    return data_type_key_map


def _get_key_to_data_type_mapping():
    """
    :return: the map with { 1000: "EXERCISE_WEAR_OS_DATA" , ... }
    """
    key_data_type_map = {}

    for key, val in DATATYPE_JSON.items():
        key_data_type_map[val[DATA_TYPE_JSON_VAL_KEY]] = key

    return key_data_type_map


def _get_data_type_to_proto_file_mapping():
    """
    :return: the map with { "EXERCISE_WEAR_OS_DATA": "Running/exercise_wear_os_data_pb2.py", ... }
    """
    proto_file_type_map = {}

    for key, val in DATATYPE_JSON.items():
        proto_file_type_map[key] = val[DATA_TYPE_JSON_VAL_PROTO_FILE]

    return proto_file_type_map


def _get_proto_file_to_data_type_mapping():
    """
    :return: the map with { "exercise_wear_os_data_pb2.py": ["EXERCISE_WEAR_OS_DATA", ...], ... }
    """
    proto_file_data_type_map = {}

    for key, val in DATATYPE_JSON.items():
        proto_file = val[DATA_TYPE_JSON_VAL_PROTO_FILE]

        # remove any directory path (e.g., "Running/exercise_wear_os_data_pb2.py" to "exercise_wear_os_data_pb2.py")
        proto_file = proto_file.split("/")[-1]

        if proto_file not in proto_file_data_type_map:
            proto_file_data_type_map[proto_file] = []

        proto_file_data_type_map[proto_file].append(key)

    return proto_file_data_type_map


# return
def _get_service_to_data_type_mapping():
    """
    :return: the map with { "service:running": ["EXERCISE_WEAR_OS_DATA", ...], ... }
    """
    service_data_type_map = {}

    for key, val in DATATYPE_JSON.items():
        for component in val[DATA_TYPE_JSON_VAL_COMPONENTS]:
            if component not in service_data_type_map:
                service_data_type_map[component] = []

            service_data_type_map[component].append(key)

    return service_data_type_map


DATATYPE_JSON = _get_data_type_json()

DATATYPE_TO_KEY_MAP = _get_data_type_to_key_mapping()
KEY_TO_DATATYPE_MAP = _get_key_to_data_type_mapping()

DATATYPE_TO_PROTO_MAP = _get_data_type_to_proto_file_mapping()
PROTO_TO_DATATYPE_MAP = _get_proto_file_to_data_type_mapping()

SERVICE_TO_DATATYPE_MAP = _get_service_to_data_type_mapping()


########################################################
################# Helper Functions #####################
########################################################


def get_key_by_instance(proto):
    """
    :param proto:
    :return: the first key number of the proto instance (DO NOT USE THIS if there are multiple proto files with the same key number)

    Example Usage:
        running_live_data_proto = running_live_data.pb2.RunningLiveData()
        get_key_by_instance(running_data_proto)  # Returns the key number, 1001
    """

    _type = str(type(proto)).split("'")[1]
    _type = _type.split(".")[0]

    proto_file = _type + ".py"
    datatype_names = PROTO_TO_DATATYPE_MAP.get(proto_file)

    if datatype_names is None or len(datatype_names) != 1:
        _logger.warn("Cannot find ONE datatype name for proto file {proto_file}", proto_file=proto_file)
    datatype_name = datatype_names[0]  # get the first datatype name

    return get_key_by_name(datatype_name)


def get_key_by_name(data_type_name):
    return DATATYPE_TO_KEY_MAP[data_type_name]


def get_name_by_key(data_type_key):
    return KEY_TO_DATATYPE_MAP[data_type_key]


def get_proto_func_by_key(data_type_key):
    datatype_name = get_name_by_key(data_type_key)
    proto_file = DATATYPE_TO_PROTO_MAP[datatype_name]

    # remove last 3 characters, that is, .py
    submod_name = proto_file[:-3]
    # change the directory format for import (i.e., replace "/" with ".")
    submod_name = submod_name.replace("/", ".")
    submod_name = f"{_PROTO_FILE_IMPORT_PATH}.{submod_name}"
    submod = importlib.import_module(submod_name)

    return getattr(submod, dir(submod)[1])


def wrap_socket_message_with_metadata(data, data_type=None):
    _data_type = data_type if data_type else get_key_by_instance(data)

    socket_data = socket_data_pb2.SocketData(
        data_type=_data_type,
        data=data.SerializeToString()
    )

    return socket_data.SerializeToString()


def decode_websocket_data(raw_data):
    if not raw_data or isinstance(raw_data, str):
        _logger.warn("Received data is not a valid socket_data instance")
        return None, None

    try:
        msg = socket_data_pb2.SocketData()
        msg.ParseFromString(raw_data)

        socket_data_type = msg.data_type
        socket_data = msg.data
    except DecodeError as e:
        _logger.warn("Error decoding protobuf message : {exc}", exc=str(e))
        return None, None

    try:
        proto_func = get_proto_func_by_key(socket_data_type)

        if not proto_func:
            _logger.error(
                "Unknown {socket_data_type} protobuf message received", socket_data_type=socket_data_type)
            return None, None

        data = proto_func()
        data.ParseFromString(socket_data)

        return socket_data_type, data
    except DecodeError as e:
        _logger.error(
            "Error decoding protobuf type {socket_data_type} : {e}", socket_data_type=socket_data_type, e=str(e))
        return None, None


# NOTE: Data is pickled when added to the shared memory (See: WebsocketWidget)
# Protobuf cannot be pickled -> Protobuf data is converted to dictionary in widget
# -> Use this function to convert back to Protobuf
def convert_json_to_protobuf(data_type, json_data):
    try:
        proto_func = get_proto_func_by_key(data_type)

        if not proto_func:
            _logger.error("Unknown {data_type} protobuf message received", data_type=data_type)
            return None

        proto_data = json_format.ParseDict(json_data, proto_func())

        return proto_data
    except json_format.ParseError as e:
        _logger.error("Error decoding protobuf message : {exc}", exc=str(e))
        return None
