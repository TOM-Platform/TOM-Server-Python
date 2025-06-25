from .pandalens_enum import PandaLensState, PandaLensAction


# Utility functions to manage state
def get_init_state():
    return PandaLensState.SERVER_OBSERVING_STATE


def get_next_state(curr_state, client_action=None):
    if curr_state is PandaLensState.SERVER_OBSERVING_STATE:
        if client_action is PandaLensAction.CLIENT_INTEREST_CAMERA_PRESS:
            return PandaLensState.SERVER_QA_STATE_USER_INITIATE
        if client_action is PandaLensAction.CLIENT_INTEREST_USER_SPEAK:
            return PandaLensState.SERVER_QA_STATE_USER_INITIATE
        if client_action is PandaLensAction.CLIENT_INTEREST_SYSTEM_DETECT:
            return PandaLensState.SERVER_QA_STATE_SYSTEM_INITIATE
        if client_action is PandaLensAction.CLIENT_SUMMARY_PRESS:
            return PandaLensState.SERVER_BLOGGING_STATE

    if curr_state is PandaLensState.SERVER_QA_STATE_SYSTEM_INITIATE:
        if client_action is PandaLensAction.CLIENT_INTEREST_USER_SPEAK:
            return PandaLensState.SERVER_QA_STATE_USER_INITIATE

    return curr_state
