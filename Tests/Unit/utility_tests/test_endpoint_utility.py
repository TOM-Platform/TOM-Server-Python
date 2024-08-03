import pytest

from Utilities import endpoint_utility, config_utility


@pytest.fixture(autouse=True)
def setup():
    config_utility.configuration = {
        "channels": ["input:name", "input2:name2"],
        "channel-entrypoints": {
            "input:name": "module.class.entryfunc",
            "input2:name2": "module2.class2.entryfunc2"
        },
        "channel-pipes": {
            "input:name": ["input2:name2"]
        }
    }


def test_get_entry_func_of_if_no_component_type():
    component = "input:name"

    assert endpoint_utility.get_entry_func_of(component) == "entryfunc"


def test_get_entry_func_of_if_component_type():
    component = "input:name"
    component_type = "input"

    assert endpoint_utility.get_entry_func_of(
        component, component_type) == "entryfunc"


def test_get_class_of_if_no_component_type():
    component = "input:name"

    assert endpoint_utility.get_class_of(component) == "class"


def test_get_class_of_if_component_type():
    component = "input:name"
    component_type = "input"

    assert endpoint_utility.get_class_of(component, component_type) == "class"


def test_get_entrypoint_of():
    component = "input:name"

    assert endpoint_utility.get_entrypoint_of(
        component) == "Widgets.module"
