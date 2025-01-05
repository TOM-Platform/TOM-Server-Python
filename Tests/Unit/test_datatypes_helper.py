import pytest

from DataFormat import datatypes_helper

# Hack to set the _DATA_TYPE_JSON variable for testing
mocked_datatype_json = {
    "data": {
        "key": 1000,
        "proto_file": "file.py",
        "components": ["service:testService"],
    }
}


# Mock the datatypes_helper module
@pytest.fixture
def mock_datatypes_helper(mocker):
    mocker.patch.object(datatypes_helper, "DATATYPE_JSON", mocked_datatype_json)
    mocker.patch.object(
        datatypes_helper,
        "DATATYPE_TO_KEY_MAP",
        datatypes_helper._get_data_type_to_key_mapping(),
    )
    mocker.patch.object(
        datatypes_helper,
        "KEY_TO_DATATYPE_MAP",
        datatypes_helper._get_key_to_data_type_mapping(),
    )
    mocker.patch.object(
        datatypes_helper,
        "DATATYPE_TO_PROTO_MAP",
        datatypes_helper._get_data_type_to_proto_file_mapping(),
    )
    mocker.patch.object(
        datatypes_helper,
        "PROTO_TO_DATATYPE_MAP",
        datatypes_helper._get_proto_file_to_data_type_mapping(),
    )


def test__get_data_type_to_key_mapping(mock_datatypes_helper):
    expected = {"data": 1000}

    assert datatypes_helper.DATATYPE_TO_KEY_MAP == expected


def test__get_key_to_data_type_mapping(mock_datatypes_helper):
    expected = {1000: "data"}

    assert datatypes_helper.KEY_TO_DATATYPE_MAP == expected


def test__get_data_type_to_proto_file_mapping(mock_datatypes_helper):
    expected = {"data": "file.py"}

    assert datatypes_helper.DATATYPE_TO_PROTO_MAP == expected


def test__get_proto_file_to_data_type_mapping(mock_datatypes_helper):
    expected = {"file.py": ["data"]}

    assert datatypes_helper.PROTO_TO_DATATYPE_MAP == expected


def test_get_key_by_name(mock_datatypes_helper):
    assert datatypes_helper.get_key_by_name("data") == 1000
