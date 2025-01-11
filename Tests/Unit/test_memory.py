import multiprocessing

import pytest
from unittest import TestCase

from Memory import Memory


@pytest.fixture(autouse=True)
def teardown():
    # Reset Memory data
    Memory.close()
    Memory.init()


def test_get_shared_memory_if_memory_not_initialised():
    Memory.close()

    assert len(Memory.get_shared_memory()) == 0


def test_update_shared_memory_if_memory_not_initialised():
    Memory.close()

    message = {
        "item1": "value1",
        "item2": "value2",
        "item3": "value3",
        "item4": "value4",
    }

    Memory.update_shared_memory(message)

    assert Memory.get_shared_memory_item("item1") == "value1"
    assert Memory.get_shared_memory_item("item2") == "value2"
    assert Memory.get_shared_memory_item("item3") == "value3"
    assert Memory.get_shared_memory_item("item4") == "value4"


def test_update_shared_memory_if_memory_initialised():
    message = {
        "item11": "value1",
        "item21": "value2",
        "item31": "value3",
        "item41": "value4",
    }

    Memory.update_shared_memory(message)

    assert Memory.get_shared_memory_item("item11") == "value1"
    assert Memory.get_shared_memory_item("item21") == "value2"
    assert Memory.get_shared_memory_item("item31") == "value3"
    assert Memory.get_shared_memory_item("item41") == "value4"


def test_update_shared_memory_with_ignored_keys():
    message = {
        "origin": "Something",
        "timestamp": "Time",
        "item1": "value1"
    }

    Memory.update_shared_memory(message)

    assert Memory.get_shared_memory_item("item1") == "value1"
    assert Memory.get_shared_memory_item("origin") is None
    assert Memory.get_shared_memory_item("timestamp") is None


def test_update_shared_memory_item_if_memory_not_initialised():
    Memory.close()

    key_name = "Key1"
    value = "Value1"

    Memory.update_shared_memory_item(key_name, value)

    assert Memory.get_shared_memory_item(key_name) == value


def test_update_shared_memory_item_if_memory_initialised():
    key_name = "Key2"
    value = "Value2"

    Memory.update_shared_memory_item(key_name, value)

    assert Memory.get_shared_memory_item(key_name) == value


def test_update_shared_memory_item_with_ignored_keys():
    key_name = "origin"
    value = "Value"

    Memory.update_shared_memory_item(key_name, value)

    assert Memory.get_shared_memory_item(key_name) is None


def func():
    x = 10
    Memory.update_shared_memory_item("x", x)


def test_shared_memory_value_exists_across_processes():
    Memory.close()
    Memory.init()

    p = multiprocessing.Process(target=func)
    p.start()

    p.join()

    assert Memory.get_shared_memory_item("x") == 10


def worker(id):
    Memory.update_shared_memory_item(f"task_{id}", id)


def test_shared_memory_value_exists_across_multi_processes():
    Memory.close()
    Memory.init()

    # Create and start worker processes
    processes = [multiprocessing.Process(target=worker, args=(i,)) for i in range(4)]
    for p in processes:
        p.start()

    for p in processes:
        p.join()

    result = {
        "task_0": 0,
        "task_1": 1,
        "task_2": 2,
        "task_3": 3
    }
    print(dict(Memory.get_shared_memory()))
    TestCase().assertDictEqual(dict(Memory.get_shared_memory()), result)
