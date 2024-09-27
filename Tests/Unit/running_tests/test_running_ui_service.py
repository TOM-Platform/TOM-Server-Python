import pytest

from Services.learning_service.learning_keys import REQUEST_LEARNING_DATA
from Services.running_service.running_data_handler import (
    build_running_live_unit,
    build_running_summary_unit,
    build_running_type_position_mapping,
    build_running_target_data,
)
from Services.running_service.running_keys import (
    REQUEST_RUNNING_SUMMARY_DATA,
    DEBUG_NONE_DATATYPE,
    DEBUG_UNSUPPORTED_DATATYPE,
    REQUEST_RUNNING_LIVE_UNIT,
    RUNNING_LIVE_UNIT,
    REQUEST_RUNNING_SUMMARY_UNIT,
    RUNNING_SUMMARY_UNIT,
    REQUEST_RUNNING_TYPE_POSITION_MAPPING,
    REQUEST_RUNNING_TARGET_DATA,
    RUNNING_TYPE_POSITION_MAPPING_DATA,
    RUNNING_TARGET_DATA,
)
from Services.running_service.running_service_params import (
    RunningUnitParams,
    SummaryUnitParams,
    DistanceTrainingParams,
    SpeedTrainingParams,
)
from Tests.Integration.test_db_util import set_test_db_environ

set_test_db_environ()
from Services.running_service.running_ui_service import RunningUiService

mock_running_ui_service = RunningUiService("RunningUiService")
from Utilities import logging_utility

_logger = logging_utility.setup_logger(__name__)


def test_running_ui_init():
    assert mock_running_ui_service.running_service is None
    assert mock_running_ui_service.name == "RunningUiService"


def test_get_ui_config_none(caplog):
    with caplog.at_level(_logger.DEBUG):
        result, result_type = mock_running_ui_service.get_ui_config(None)
    assert result is None
    assert result_type is None
    assert DEBUG_NONE_DATATYPE in caplog.text


def test_get_ui_config_unsupported(caplog):
    with caplog.at_level(_logger.DEBUG):
        result, result_type = mock_running_ui_service.get_ui_config(
            REQUEST_RUNNING_SUMMARY_DATA
        )
    assert result is None
    assert result_type is None
    assert DEBUG_UNSUPPORTED_DATATYPE in caplog.text


def test_get_ui_config_running_unit():
    result, result_type = mock_running_ui_service.get_ui_config(
        REQUEST_RUNNING_LIVE_UNIT
    )
    assert result == build_running_live_unit(
        RunningUnitParams.distance,
        RunningUnitParams.heart_rate,
        RunningUnitParams.speed,
        RunningUnitParams.duration,
    )
    assert result_type is RUNNING_LIVE_UNIT


def test_get_ui_config_summary_unit():
    result, result_type = mock_running_ui_service.get_ui_config(
        REQUEST_RUNNING_SUMMARY_UNIT
    )
    assert result == build_running_summary_unit(
        distance=SummaryUnitParams.distance,
        speed=SummaryUnitParams.speed,
        duration=SummaryUnitParams.duration,
    )
    assert result_type is RUNNING_SUMMARY_UNIT


def test_get_ui_config_position_mapping():
    result, result_type = mock_running_ui_service.get_ui_config(
        REQUEST_RUNNING_TYPE_POSITION_MAPPING
    )
    assert result == build_running_type_position_mapping()
    assert result_type is RUNNING_TYPE_POSITION_MAPPING_DATA


def test_get_ui_config_target_data():
    result, result_type = mock_running_ui_service.get_ui_config(
        REQUEST_RUNNING_TARGET_DATA
    )
    assert result == build_running_target_data(
        distance=DistanceTrainingParams.target_distance,
        speed=SpeedTrainingParams.target_speed,
    )
    assert result_type is RUNNING_TARGET_DATA


def test_get_ui_config_unknown_data(caplog):
    with caplog.at_level(_logger.ERROR):
        result, result_type = mock_running_ui_service.get_ui_config(
            REQUEST_LEARNING_DATA
        )
    assert result is None
    assert result_type is None
    assert f"--- Unknown datatype: REQUEST_LEARNING_DATA\n" in caplog.text
