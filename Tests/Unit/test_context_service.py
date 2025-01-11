from unittest import mock

import pytest

from Tests.Integration.test_db_util import set_test_db_environ

set_test_db_environ()

import base_keys
from Memory import Memory
from Utilities import config_utility
from Services.context_service.context_service import ContextService


class MockClass:
    def __init__(self) -> None:
        pass

    def mock_func(self):
        pass


component_instance = MockClass


@pytest.fixture(autouse=True)
def setup():
    config_utility.configuration = {
        "channels": ["input:name", "input2:name2"],
        "channel-entrypoints": {
            "input:name": "module.class.entryfunc",
            "input:name2": "module2.class2.entryfunc2"
        },
        "channel-exitpoints": {
            "input:name": "module.class.exitfunc",
            "input:name2": "module2.class2.exitfunc2"
        },
        "channel-pipes": {
            "input:name": ["input:name2"]
        }
    }

    Memory.init()
    Memory.update_shared_memory_item(base_keys.MEMORY_COMPONENT_STATUS_KEY, {})  # Initialise with an empty dictionary


@pytest.fixture(autouse=True)
def teardown():
    # Reset Memory data
    Memory._memory = None
    Memory.init()
    Memory.update_shared_memory_item(base_keys.MEMORY_COMPONENT_STATUS_KEY, {})  # Initialise with an empty dictionary


def test_run_with_no_errors():
    context_service = ContextService("name")

    with mock.patch("Utilities.endpoint_utility.get_component_instance",
                    mock.MagicMock(return_value=component_instance)):
        with mock.patch("Utilities.endpoint_utility.get_entry_func_of", mock.MagicMock(return_value="mock_func")):
            data = {
                "websocket_message": {
                    "detail": "input:name2"
                }
            }

            try:
                context_service.run(data)
            except Exception:
                pytest.fail("Unexpected Error Occurred")
