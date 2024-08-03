import pytest

from Memory import Memory
from Tests.Integration.test_db_util import set_test_db_environ
from base_keys import COMPONENT_NOT_STARTED_STATUS

set_test_db_environ()
from Services.running_service.running_service import RunningService

mock_running_service = RunningService(name="RunningService")


def test_running_service_init():
    assert mock_running_service.name == "RunningService"
    assert mock_running_service.route_selection_service is None
    assert mock_running_service.running_coach_service is None
    assert mock_running_service.running_ui_service is None
    assert mock_running_service.training_mode_selection_service is None
    assert mock_running_service.get_component_status() == COMPONENT_NOT_STARTED_STATUS
    assert mock_running_service.received_wear_os_data is False
