import pytest
from unittest.mock import Mock, call
from Services.martial_arts_service.martial_arts_sequence_service import MartialArtsSequenceService
from Services.martial_arts_service.martial_arts_keys import MA_SEQUENCE_DATA


@pytest.fixture
def mock_martial_arts_service():
    return Mock()


@pytest.fixture
def sequence_service(mock_martial_arts_service):
    return MartialArtsSequenceService(mock_martial_arts_service)


def test_generate_next_sequence_not_empty_pool(sequence_service, mock_martial_arts_service):
    # Mock sequence pool
    sequence_service.sequence_pool = ["sequence1"]

    # Call the method
    sequence_service.generate_next_sequence()

    # Assert that send_to_component method was called with the correct arguments
    mock_martial_arts_service.send_to_component.assert_called_once_with(
        websocket_message="sequence1",
        websocket_data_type=MA_SEQUENCE_DATA
    )


def test_generate_next_sequence_empty_pool(sequence_service, mock_martial_arts_service):
    # Mock empty sequence pool
    sequence_service.sequence_pool = []

    # Call the method
    result = sequence_service.generate_next_sequence()

    # Assert that send_to_component method was not called and returned None
    mock_martial_arts_service.send_to_component.assert_not_called()
    assert result is None


def test_generate_next_sequence_multiple_calls(sequence_service, mock_martial_arts_service):
    # Mock sequence pool
    sequence_service.sequence_pool = ["sequence1"]

    # Call the method multiple times
    sequence_service.generate_next_sequence()
    sequence_service.generate_next_sequence()
    sequence_service.generate_next_sequence()

    # Assert that send_to_component method was called three times with different sequences
    mock_martial_arts_service.send_to_component.assert_has_calls([
        call(websocket_message="sequence1", websocket_data_type=MA_SEQUENCE_DATA),
        call(websocket_message="sequence1", websocket_data_type=MA_SEQUENCE_DATA),
        call(websocket_message="sequence1", websocket_data_type=MA_SEQUENCE_DATA),
    ], any_order=True)
