import pytest

from Memory import Memory
from Tests.Integration.test_db_util import set_test_db_environ

set_test_db_environ()
from base_component import BaseComponent

base_component = BaseComponent(name="Test")


@pytest.fixture(autouse=True)
def teardown():
    # Reset memory after each test
    Memory.close()


def test_set_memory_data():
    Memory.init()

    key_name = "Key"
    value = "Value"

    base_component.set_memory_data(key_name, value)

    assert Memory.get_shared_memory_item(key_name) == value


def test_get_memory_data():
    Memory.init()

    key_name = "Key"
    value = "Value"

    Memory.update_shared_memory_item(key_name, value)

    assert base_component.get_memory_data(key_name) == value
