import pytest

from Utilities import config_utility


@pytest.fixture(autouse=True)
def teardown():
    # NOTE: Reset the configuration in the utility between tests
    config_utility.configuration = {}


def test_add_channel_to_configuration_if_no_item():
    config_utility.configuration = {
        "channels": ["test", "item"]
    }

    config_utility.add_channel_to_configuration("unknown")

    expected_result = {
        "channels": ["test", "item", "unknown"]
    }

    assert expected_result == config_utility.configuration


def test_add_channel_to_configuration_if_has_item():
    config_utility.configuration = {
        "channels": ["test", "item"]
    }

    config_utility.add_channel_to_configuration("item")

    expected_result = {
        "channels": ["test", "item"]
    }

    assert expected_result == config_utility.configuration


def test_add_entrypoint_to_configuration_if_no_item():
    config_utility.configuration = {
        "channel-entrypoints": {
            "test_key": "test_val"
        }
    }

    test_component = {
        "endpoint": "val"
    }

    config_utility.add_entrypoint_to_configuration(test_component, "item")

    expected_result = {
        "channel-entrypoints": {
            "test_key": "test_val",
            "item": "val"
        }
    }

    assert expected_result == config_utility.configuration


def test_add_entrypoint_to_configuration_if_has_item():
    config_utility.configuration = {
        "channel-entrypoints": {
            "test_key": "test_val"
        }
    }

    test_component = {
        "endpoint": "val"
    }

    config_utility.add_entrypoint_to_configuration(test_component, "test_key")

    expected_result = {
        "channel-entrypoints": {
            "test_key": "test_val",
        }
    }

    assert expected_result == config_utility.configuration


def test_add_pipe_to_configuration():
    config_utility.configuration = {
        "channel-pipes": {
            "test_key": ["something", "another"]
        }
    }

    test_component = {
        "next": ["one"]
    }

    config_utility.add_pipe_to_configuration(test_component, "test_key")

    expected_result = {
        "channel-pipes": {
            "test_key": ["something", "another", "one"]
        }
    }

    assert expected_result == config_utility.configuration


def test_add_pipe_to_configuration_if_pipe_already_exists():
    config_utility.configuration = {
        "channel-pipes": {
            "test_key": ["something", "another"]
        }
    }

    test_component = {
        "next": ["one", "and", "another"]
    }

    config_utility.add_pipe_to_configuration(test_component, "test_key")

    expected_result = {
        "channel-pipes": {
            "test_key": ["something", "another", "one", "and"]
        }
    }

    assert expected_result == config_utility.configuration


def test_add_pipe_to_configuration_if_no_next():
    config_utility.configuration = {
        "channel-pipes": {
            "test_key": ["something", "another"]
        }
    }

    test_component = {}

    config_utility.add_pipe_to_configuration(test_component, "test_key")

    expected_result = {
        "channel-pipes": {
            "test_key": ["something", "another"]
        }
    }

    assert expected_result == config_utility.configuration


def test_get_channel_entrypoints():
    config_utility.configuration = {
        "channel-entrypoints": {
            "test_key": "test_val"
        }
    }

    expected_result = {
        "test_key": "test_val"
    }

    assert expected_result == config_utility.get_channel_entrypoints()


def test_get_channel_pipes():
    config_utility.configuration = {
        "channel-pipes": {
            "test_key": ["something", "another"]
        }
    }

    expected_result = {
        "test_key": ["something", "another"]
    }

    assert expected_result == config_utility.get_channel_pipes()
