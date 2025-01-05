import pytest

import base_keys
from DataFormat import datatypes_helper
from Services.memory_assistance_service.memory_assistance_service import MemoryAssistanceService


@pytest.fixture
def memory_service():
    service = MemoryAssistanceService("test_service")
    return service


def test_initialization(memory_service):
    assert memory_service.last_image_saved_millis == 0
    assert memory_service.name == "test_service"


def test_handle_speech_data(memory_service):
    raw_data = {
        base_keys.ORIGIN_KEY: base_keys.WEBSOCKET_WIDGET,
        base_keys.WEBSOCKET_MESSAGE: {"voice": "dummy_text"},
        base_keys.WEBSOCKET_DATATYPE: datatypes_helper.get_key_by_name("SPEECH_INPUT_DATA")
    }
    result = memory_service.run(raw_data)
    assert result == "dummy_text"
