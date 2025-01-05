import pytest
from DataFormat.ProtoFiles.Common import key_event_data_pb2, key_event_type_pb2
import base_keys
from Services.memory_assistance_service.memory_assistance_data_handler import get_key_event_type


def test_get_key_event_type_press():
    key_event_data = key_event_data_pb2.KeyEventData(code=0, type=key_event_type_pb2.KeyEventType.PRESS, name="")

    # Call the function and verify the result
    result = get_key_event_type(key_event_data)
    assert result == base_keys.KEYBOARD_EVENT_PRESS


def test_get_key_event_type_release():
    key_event_data = key_event_data_pb2.KeyEventData(code=0, type=key_event_type_pb2.KeyEventType.RELEASE, name="")

    # Call the function and verify the result
    result = get_key_event_type(key_event_data)
    assert result == base_keys.KEYBOARD_EVENT_RELEASE


def test_get_key_event_type_default():
    key_event_data = key_event_data_pb2.KeyEventData(code=0, name="")
    key_event_data.ClearField("type")  # Explicitly unset the type field if necessary

    # Call the function and verify the result
    result = get_key_event_type(key_event_data)
    assert result == base_keys.KEYBOARD_EVENT_PRESS
