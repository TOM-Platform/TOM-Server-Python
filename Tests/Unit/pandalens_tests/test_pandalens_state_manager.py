import Services.pandalens_service.pandalens_state_manager as pandalens_mgr
from Services.pandalens_service.pandalens_enum import PandaLensAction, PandaLensState


def test_get_next_state_observing_to_qna():
    # Arrange
    curr_state = PandaLensState.SERVER_OBSERVING_STATE
    action_camera_press = PandaLensAction.CLIENT_CAMERA_PRESS
    action_interest = PandaLensAction.CLIENT_INTEREST

    # Act & Assert
    assert pandalens_mgr.get_next_state(curr_state, action_camera_press) == PandaLensState.SERVER_QNA_STATE
    assert pandalens_mgr.get_next_state(curr_state, action_interest) == PandaLensState.SERVER_QNA_STATE


def test_get_next_state_observing_to_blog():
    # Arrange
    curr_state = PandaLensState.SERVER_OBSERVING_STATE
    action_summary_press = PandaLensAction.CLIENT_SUMMARY_PRESS

    # Act & Assert
    assert pandalens_mgr.get_next_state(curr_state, action_summary_press) == PandaLensState.SERVER_BLOGGING_STATE


def test_get_next_state_no_transition():
    # Arrange
    curr_state = PandaLensState.SERVER_QNA_STATE
    action_camera_press = PandaLensAction.CLIENT_CAMERA_PRESS

    # Act & Assert
    assert pandalens_mgr.get_next_state(curr_state, action_camera_press) == curr_state


def test_reset():
    # Act & Assert
    assert pandalens_mgr.reset() == PandaLensState.SERVER_OBSERVING_STATE
