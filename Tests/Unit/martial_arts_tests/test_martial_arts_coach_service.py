import pytest
from unittest.mock import Mock
from Services.martial_arts_service.martial_arts_coach_service import MartialArtsCoachService
from Services.martial_arts_service.martial_arts_keys import MA_FEEDBACK_LIVE_DATA
import Services.martial_arts_service.const as const
from DataFormat.ProtoFiles.Common import request_data_pb2


@pytest.fixture
def mock_martial_arts_service():
    return Mock()


@pytest.fixture
def coach_service(mock_martial_arts_service):
    return MartialArtsCoachService(mock_martial_arts_service)


def test_send_live_feedback(coach_service, mock_martial_arts_service):
    # Mock the required objects
    live_feedback = "test_feedback"
    request_data = request_data_pb2.RequestData()

    # Call the method
    coach_service.send_live_feedback(live_feedback)

    request_data.detail = live_feedback
    # Assert that the expected methods were called with the correct arguments
    assert mock_martial_arts_service.send_to_component.called
    mock_martial_arts_service.send_to_component.assert_called_with(
        websocket_message=request_data,
        websocket_datatype=MA_FEEDBACK_LIVE_DATA
    )
    assert live_feedback in coach_service.feedback_set


def test_analyse_live_data(coach_service):
    # Prepare dummy decoded data
    decoded_data_good = Mock()
    decoded_data_good.collision_data.collision_point.x = 0
    decoded_data_good.collision_data.collision_point.y = 0
    decoded_data_good.collision_data.pad_position.x = 0
    decoded_data_good.collision_data.pad_position.y = 0
    decoded_data_good.collision_data.distance_to_target = const.DISTANCE_TO_TARGET_FEEDBACK_THRESHOLD
    decoded_data_good.collision_data.angle = const.ANGLE_FEEDBACK_THRESHOLD_LOWER

    # Call the method for good feedback
    result_good = coach_service.analyse_live_data(decoded_data_good)

    # Assert the result is as expected for good feedback
    assert result_good == const.GOOD

    # Prepare dummy decoded data for off-target feedback
    decoded_data_off_target = Mock()
    decoded_data_off_target.collision_data.collision_point.x = 0
    decoded_data_off_target.collision_data.collision_point.y = 0
    decoded_data_off_target.collision_data.pad_position.x = 0
    decoded_data_off_target.collision_data.pad_position.y = 0
    decoded_data_off_target.collision_data.distance_to_target = const.DISTANCE_TO_TARGET_FEEDBACK_THRESHOLD
    decoded_data_off_target.collision_data.angle = const.ANGLE_FEEDBACK_THRESHOLD_LOWER - 1

    # Call the method for off-target feedback
    result_off_target = coach_service.analyse_live_data(
        decoded_data_off_target)

    # Assert the result is as expected for off-target feedback
    assert result_off_target == const.PUNCH_NOT_STRAIGHT

    # Prepare dummy decoded data for another off-target feedback scenario
    decoded_data_off_target_2 = Mock()
    decoded_data_off_target_2.collision_data.collision_point.x = 1
    decoded_data_off_target_2.collision_data.collision_point.y = 0
    decoded_data_off_target_2.collision_data.pad_position.x = 0
    decoded_data_off_target_2.collision_data.pad_position.y = 0
    decoded_data_off_target_2.collision_data.distance_to_target = const.DISTANCE_TO_TARGET_FEEDBACK_THRESHOLD + 1
    decoded_data_off_target_2.collision_data.angle = const.ANGLE_FEEDBACK_THRESHOLD_HIGHER - 1

    # Call the method for another off-target feedback scenario
    result_off_target_2 = coach_service.analyse_live_data(
        decoded_data_off_target_2)

    # Assert the result is as expected for the second off-target feedback scenario
    assert result_off_target_2 == const.PUNCH_LEFT


def test_categorize_feedback(coach_service):
    # Test for GOOD feedback
    assert coach_service.categorize_feedback(const.GOOD) == const.GOOD_PUNCH

    # Test for OFF_TARGET feedback
    for feedback in const.OFF_TARGET_FEEDBACK:
        assert coach_service.categorize_feedback(feedback) == const.OFF_TARGET

    # Test for BAD_ANGLE feedback
    assert coach_service.categorize_feedback(
        "some_bad_angle_feedback") == const.BAD_ANGLE
