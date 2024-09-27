import pytest
from unittest.mock import Mock
from Services.martial_arts_service.martial_arts_speech_service import MartialArtsSpeechService
from Services.martial_arts_service.martial_arts_keys import SPEECH_INPUT_DATA
from Services.martial_arts_service.martial_arts_voice_commands import SET_DURATION_CMD, SET_INTERVAL_CMD
from DataFormat.ProtoFiles.Common import speech_data_pb2


@pytest.fixture
def mock_martial_arts_service():
    return Mock()


@pytest.fixture
def speech_service(mock_martial_arts_service):
    return MartialArtsSpeechService(mock_martial_arts_service)


def test_handle_speech_input_duration(speech_service, mock_martial_arts_service):
    # Mock speech input data
    speech_input_data = "Set time 10 minutes"

    # Call the method
    speech_service.handle_speech_input(speech_input_data)

    # Assert that send_to_component method was called with the correct arguments
    mock_martial_arts_service.send_to_component.assert_called_once_with(
        websocket_message=speech_data_pb2.SpeechData(voice=SET_DURATION_CMD + ";10"),
        websocket_datatype=SPEECH_INPUT_DATA
    )


def test_handle_speech_input_interval(speech_service, mock_martial_arts_service):
    # Mock speech input data
    speech_input_data = "Set interval 30 seconds"

    # Call the method
    speech_service.handle_speech_input(speech_input_data)

    # Assert that send_to_component method was called with the correct arguments
    mock_martial_arts_service.send_to_component.assert_called_once_with(
        websocket_message=speech_data_pb2.SpeechData(voice=SET_INTERVAL_CMD + ";30"),
        websocket_datatype=SPEECH_INPUT_DATA
    )


def test_handle_speech_input_invalid_input(speech_service, mock_martial_arts_service):
    # Mock invalid speech input data
    speech_input_data = "Invalid speech input"

    # Call the method
    speech_service.handle_speech_input(speech_input_data)

    # Assert that send_to_component method was not called
    mock_martial_arts_service.send_to_component.assert_not_called()
