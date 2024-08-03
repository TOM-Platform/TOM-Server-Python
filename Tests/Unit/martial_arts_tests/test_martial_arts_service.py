from base_keys import ORIGIN_KEY, WEBSOCKET_WIDGET, WEBSOCKET_MESSAGE, WEBSOCKET_DATATYPE
from google.protobuf.json_format import MessageToJson
import pytest
from unittest.mock import Mock
from Services.martial_arts_service.martial_arts_service import MartialArtsService
from Services.martial_arts_service.martial_arts_keys import (
    MA_REQUEST_SEQUENCE_DATA,
    MA_METRICS_DATA,
    MA_UPDATE_SESSION_CONFIG_COMMAND,
    MA_BEGIN_SESSION_COMMAND,
    MA_END_SESSION_COMMAND,
    MA_REQUEST_CONFIG_DATA,
    SPEECH_INPUT_DATA
)

from DataFormat.ProtoFiles.MartialArts import ma_end_session_data_pb2, ma_metrics_data_pb2


@pytest.fixture
def mock_sequence_service():
    return Mock()


@pytest.fixture
def mock_coach_service():
    return Mock()


@pytest.fixture
def mock_config_service():
    return Mock()


@pytest.fixture
def mock_metrics_service():
    return Mock()


@pytest.fixture
def mock_speech_service():
    return Mock()


@pytest.fixture
def martial_arts_service(mock_sequence_service, mock_coach_service, mock_config_service, mock_metrics_service,
                         mock_speech_service):
    service = MartialArtsService(name="test_service")
    service.ma_sequence_service = mock_sequence_service
    service.ma_coach_service = mock_coach_service
    service.ma_config_service = mock_config_service
    service.ma_metrics_service = mock_metrics_service
    service.ma_speech_service = mock_speech_service
    return service


def test_run_with_websocket_sequence_request(martial_arts_service, mock_sequence_service):
    # Mock raw data
    raw_data = {
        ORIGIN_KEY: WEBSOCKET_WIDGET,
        WEBSOCKET_DATATYPE: MA_REQUEST_SEQUENCE_DATA,
        WEBSOCKET_MESSAGE: "some_message"
    }

    # Call the run method
    martial_arts_service.run(raw_data)

    # Assert that the sequence service's generate_next_sequence method was called
    mock_sequence_service.generate_next_sequence.assert_called_once()


def test_run_with_websocket_with_custom_proto_type(martial_arts_service, mock_metrics_service):
    # Mock raw data
    decoded_data = ma_end_session_data_pb2.MaEndSessionData()
    decoded_data.session_duration = "some_session_duration"
    decoded_data.interval_duration = 10.5
    decoded_data.datetime = 1234567890

    converted_data = {
        'session_duration': decoded_data.session_duration,
        'interval_duration': decoded_data.interval_duration,
        'datetime': str(decoded_data.datetime)
    }

    raw_data = {
        ORIGIN_KEY: WEBSOCKET_WIDGET,
        WEBSOCKET_DATATYPE: MA_END_SESSION_COMMAND,
        WEBSOCKET_MESSAGE: converted_data
    }

    # Call the run method
    martial_arts_service.run(raw_data)

    # Assert that the metrics service's process_save_metrics method was called
    mock_metrics_service.process_save_metrics.assert_called_once_with(
        decoded_data)
